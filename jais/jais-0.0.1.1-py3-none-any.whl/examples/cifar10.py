import torch
import torchmetrics
import torchvision
import torchvision.transforms as transforms
import torch.optim as optim
from torchsummary import summary
from jais.utils import *
from jais.train.trainer import Trainer
from jais.visualize.data import show_batch
from jais.models.example import Net
from jais.train.lr_scheduler import OptmWithLRSWrapper

CNF, LOG = load_default_configs()
LOG.info("Running CIFAR10 experiment...")

device, cuda_ids = get_device()
LOG.info(f"device = {device}")

NUM_EPOCHS = 20

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
net = Net()
# LOG.debug("Loading model summary...")
# summary(net, input_size=(3,32,32))

# LOSS
loss_fn = torch.nn.CrossEntropyLoss()

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
    # PREDICT
    outputs = self.net(inputs)
    # LOSS
    loss = self.loss_fn(outputs, targets)
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
trainer = Trainer(dls=dls, net=net,
                  loss_fn=loss_fn,
                  optm_fn=optimizer,
                  device=device,
                  metrics=metrics, logger_name='wb')
trainer.train(20)
