import os

import torch.optim
import torchvision.datasets
from torch import nn
from torch.nn import Sequential, Conv2d, MaxPool2d, Flatten, Linear
from torch.utils.data import DataLoader




class optimExModel(nn.Module):
    def __init__(self):
        super(optimExModel, self).__init__()
        self.seq = Sequential(
            Conv2d(3, 32, 5, padding=2),
            MaxPool2d(2),
            Conv2d(32, 32, 5, padding=2),
            MaxPool2d(2),
            Conv2d(32, 64, 5, padding=2),
            MaxPool2d(2),
            Flatten(),
            Linear(1024, 64),
            Linear(64, 10)
        )

    def forward(self, x):
        x = self.seq(x)
        return x


def run(gpu_id):
    os.environ['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    dataset = torchvision.datasets.CIFAR10('./dataset', train=False, transform=torchvision.transforms.ToTensor(),
                                           download=True)
    dataloader = DataLoader(dataset, batch_size=64)
    loss = nn.CrossEntropyLoss()

    optim_ex = optimExModel()
    optim = torch.optim.SGD(optim_ex.parameters(), lr=0.01)
    for epoch in range(10):
        loss_sum = 0.0
        for data in dataloader:
            img, target = data
            output = optim_ex(img)
            result_loss = loss(output, target)
            optim.zero_grad()
            result_loss.backward()
            optim.step()
            loss_sum += result_loss

        print(loss_sum)


