import time
import torch
import torchmetrics
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torchsummary import summary
from pathlib import Path
from jais.utils import load_default_configs, get_device
from jais.visualize import show_batch
from jais.models import Net
from jais.train import *


RANK = 0
WORLD_SIZE = 1
NUM_EPOCHS = 10
MIXUP_ALPHA = 0.2
LABEL_SMOOTH = True
SUPERLOSS = True

os.environ['MASTER_ADDR'] = 'localhost'
os.environ['MASTER_PORT'] = '12356'

CNF, LOG = load_default_configs()
LOG.info("Running CIFAR10 experiment...")

training_logs_filename = f"{Path(__file__).stem}@{time.time()}"
device, cuda_ids = get_device()
dist.init_process_group('nccl', rank=RANK, world_size=WORLD_SIZE)
LOG.info(f"device = {device}")


train_tfms = transforms.Compose([
    transforms.AutoAugment(),
    transforms.ToTensor(),
    transforms.Normalize(CNF.data.mean, CNF.data.std)
])
val_tfms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(CNF.data.mean, CNF.data.std)
])

# DATASET
classes = ('plane', 'car', 'bird', 'cat', 'deer',
           'dog', 'frog', 'horse', 'ship', 'truck')
n_classes = len(classes)

trainset = torchvision.datasets.CIFAR10(root=CNF.paths.data_dir, train=True,
                                        download=True, transform=train_tfms)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=CNF.bs,
                                          shuffle=True, num_workers=2)
testset = torchvision.datasets.CIFAR10(root=CNF.paths.data_dir, train=False,
                                       download=True, transform=val_tfms)
testloader = torch.utils.data.DataLoader(testset, batch_size=CNF.bs,
                                         shuffle=False, num_workers=2)

# get some random training images
images, labels = next(iter(trainloader))
LOG.debug(f"IMAGES = {images.shape}")
LOG.debug(f"LABELS = {labels}")

# show_batch(images.permute(0,2,3,1), labels)

dls = {'train': trainloader, 'val': testloader}
NUM_BATCHES = len(trainset) // CNF.bs
# MODEL
LOG.debug("Loading model...")
net = Net().to(device)
net = nn.SyncBatchNorm.convert_sync_batchnorm(net)
net = DDP(net, device_ids=cuda_ids, find_unused_parameters=True)
# LOG.debug("Loading model summary...")
# summary(net, input_size=(3,32,32))

# LOSS
if LABEL_SMOOTH:
    if SUPERLOSS:
        from jais.train.losses import LabelSmoothingCEWithSuperLoss
        loss_fn = LabelSmoothingCEWithSuperLoss(classes=n_classes, device=device)
    else:
        from jais.train.losses import LabelSmoothingCE
        loss_fn = LabelSmoothingCE(classes=n_classes)
else:
    loss_fn = torch.nn.CrossEntropyLoss()
LOG.info(f"loss function = `{loss_fn.__class__.__name__}`")

# OPTIMIZER AND LR SCHEDULER
optimizer = optim.SGD(net.parameters(),
                      lr=CNF.train.lr,
                      momentum=CNF.train.mom
                      )
optimizer = OptmWithLRSWrapper(optimizer,
                               num_epochs=NUM_EPOCHS,
                               num_iters_per_epochs=NUM_BATCHES,
                               lr_range=(0.01, 1e-5))

metrics = torchmetrics.MetricCollection([
    torchmetrics.Accuracy(num_classes=n_classes, average='macro'),
    torchmetrics.Precision(num_classes=n_classes, average='macro'),
    torchmetrics.Recall(num_classes=n_classes, average='macro'),
    torchmetrics.F1(num_classes=n_classes, average='macro'),
])


def train_one_batch(self, batch):
    # DATA
    inputs, targets = batch
    inputs, targets = inputs.to(self.device), targets.to(self.device)
    inputs, targets_a, targets_b, lam = mixup_data(inputs, targets,
                                                   MIXUP_ALPHA, device)
    # PREDICT
    outputs = self.net(inputs)
    # LOSS
    # loss = self.loss_fn(outputs, targets)
    loss = mixup_criterion(self.loss_fn, outputs, targets_a, targets_b, lam)
    # BACKWARD
    self.optm_fn.zero_grad()
    loss.backward()
    self.optm_fn.step()
    return loss, outputs, targets


def val_one_batch(self, batch):
    # DATA
    inputs, targets = batch
    inputs, targets = inputs.to(self.device), targets.to(self.device)
    # PREDICT
    outputs = self.net(inputs)
    # LOSS
    loss = self.loss_fn(outputs, targets)
    return loss, outputs, targets


Trainer.train_one_batch = train_one_batch
Trainer.val_one_batch = val_one_batch
trainer = Trainer(dls=dls,
                  net=net,
                  loss_fn=loss_fn,
                  optm_fn=optimizer,
                  device=device,
                  metrics=metrics,
                  chkpt_of=[{'val_loss': 'min', 'Accuracy': 'max'}],
                  training_logger_name='wb',
                  training_logs_filename=training_logs_filename,
                  wandb_init_kwargs={'config': CNF},
                  )
trainer.train(NUM_EPOCHS)
