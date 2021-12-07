import time
import torch
import torchmetrics
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
from torchsummary import summary
from pathlib import Path
from jais.utils import load_default_configs, get_device
from jais.visualize import show_batch
from jais.models import Net
from jais.train import *


CNF, LOG = load_default_configs()
LOG.info("Running CIFAR10 experiment...")

training_logs_filename = f"{Path(__file__).stem}@{time.time()}"
device, cuda_ids = get_device()
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
trainloader = torch.utils.data.DataLoader(trainset, batch_size=CNF.train.bs,
                                          shuffle=True, num_workers=2)
testset = torchvision.datasets.CIFAR10(root=CNF.paths.data_dir, train=False,
                                       download=True, transform=val_tfms)
testloader = torch.utils.data.DataLoader(testset, batch_size=CNF.train.bs,
                                         shuffle=False, num_workers=2)

# get some random training images
images, labels = next(iter(trainloader))
LOG.debug(f"IMAGES = {images.shape}")
LOG.debug(f"LABELS = {labels}")

# show_batch(images.permute(0,2,3,1), labels)

dls = {'train': trainloader, 'val': testloader}
NUM_BATCHES = len(trainset) // CNF.train.bs
# MODEL
LOG.debug("Loading model...")
net = Net().to(device)
net = torch.nn.DataParallel(net, device_ids=cuda_ids)
# LOG.debug("Loading model summary...")
# summary(net, input_size=(3,32,32))

# LOSS
loss_fn = torch.nn.CrossEntropyLoss(label_smoothing=CNF.loss.smoothing)
LOG.info(f"loss function = `{loss_fn.__class__.__name__}`")

# OPTIMIZER AND LR SCHEDULER
if CNF.optm.name.lower() == 'sgd':
    optimizer = optim.SGD(net.parameters(),
                          lr=CNF.optm.lr,
                          momentum=CNF.optm.mom,
                          weight_decay=CNF.optm.wd,
                          nesterov=CNF.optm.nesterov)
else:
    optimizer = optim.Adam(net.parameters(),
                           lr=CNF.optm.lr,
                           betas=CNF.optm.betas,
                           weight_decay=CNF.optm.wd,
                           amsgrad=CNF.optm.amsgrad)

optimizer = OptmWithLRSWrapper(optimizer,
                               num_epochs=CNF.train.epochs,
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
                                                   CNF.train.mixup_alpha,
                                                   self.device)
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
trainer.train(CNF.train.epochs)
