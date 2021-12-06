"""
2021-10-05  13:23:39
"""
from datetime import datetime
import paddle

from paddle.nn import Conv2D, BatchNorm2D, Linear, Sequential
from paddle.vision.transforms import Compose, Normalize, RandomCrop, RandomHorizontalFlip, ToTensor
import paddle.nn.functional as F
import numpy as np

BATCHSIZE = 64
normalize = Normalize(
    mean=[0.4914, 0.4822, 0.4465],
    std=[0.2023, 0.1994, 0.2010],
    data_format='CHW'
)
train_transform = Compose([RandomCrop(32, padding=4),
                           RandomHorizontalFlip(),
                           ToTensor(),
                           normalize]
                          )
test_transform = Compose([ToTensor(), normalize])
train_dataset = paddle.vision.datasets.Cifar10(mode='train', transform=train_transform, download=True)
test_dataset = paddle.vision.datasets.Cifar10(mode='test', transform=test_transform, download=True)


class BasicBlock(paddle.nn.Layer):
    expansion = 1

    def __init__(self, in_channels, out_channels, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = Conv2D(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias_attr=False)
        self.bn1 = BatchNorm2D(out_channels)
        self.conv2 = Conv2D(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias_attr=False)
        self.bn2 = BatchNorm2D(out_channels)

        self.shortcut = Sequential()
        if stride != 1 or in_channels != self.expansion * out_channels:
            self.shortcut = Sequential(
                Conv2D(in_channels, self.expansion * out_channels, kernel_size=1, stride=stride, bias_attr=False),
                BatchNorm2D(self.expansion * out_channels)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


class EvoCNNModel(paddle.nn.Layer):
    def __init__(self):
        super(EvoCNNModel, self).__init__()

        #conv unit
        self.conv_3_128 = BasicBlock(in_channels=3, out_channels=128)
        self.conv_128_256 = BasicBlock(in_channels=128, out_channels=256)
        self.conv_256_128 = BasicBlock(in_channels=256, out_channels=128)

        #linear unit
        self.linear = Linear(4096, 10)

    def forward(self, x):
        out_0 = self.conv_3_128(x)
        out_1 = self.conv_128_256(out_0)
        out_2 = F.max_pool2d(out_1, kernel_size=2)
        out_3 = self.conv_256_128(out_2)
        out_4 = F.max_pool2d(out_3, kernel_size=2)
        out_5 = self.conv_128_256(out_4)
        out_6 = F.max_pool2d(out_5, kernel_size=2)
        out = out_6

        out = paddle.reshape(out, [out.shape[0], -1])
        out = self.linear(out)
        return out


class TrainModel(object):
    def __init__(self):
        self.train_loader = paddle.io.DataLoader(train_dataset, batch_size=BATCHSIZE, shuffle=True, drop_last=True)
        self.test_loader = paddle.io.DataLoader(test_dataset, batch_size=BATCHSIZE, shuffle=True, drop_last=True)
        self.best_acc = 0.0
        self.model = EvoCNNModel()

    def train(self, epoch):
        self.model.train()
        if epoch == 0: lr = 0.01
        if epoch > 0: lr = 0.1
        if epoch > 148: lr = 0.01
        if epoch > 248: lr = 0.001
        optimizer = paddle.optimizer.SGD(parameters=self.model.parameters(), learning_rate=lr, weight_decay=5e-4)

        for i in range(epoch):
            train_loss = list()
            train_acc = list()
            for i, data in enumerate(self.train_loader()):
                imgs, labels = data
                imgs = paddle.to_tensor(imgs)
                labels = paddle.to_tensor(labels)
                labels = paddle.reshape(labels, [BATCHSIZE, 1])

                pred = self.model(imgs)
                loss = F.cross_entropy(pred, labels)
                train_loss.append(loss.numpy())
                loss.backward()
                optimizer.step()
                optimizer.clear_grad()
                acc = paddle.metric.accuracy(input=pred, label=labels)
                if i % 100 == 0:
                    print('epoch:{} batch:{}  loss:{}   acc:{} '.format(epoch + 1, i * BATCHSIZE, loss, acc))
                train_acc.append(acc.numpy())

            loss_mean = np.mean(train_loss)
            acc_mean = np.mean(train_acc)
            if acc_mean > self.best_acc:
                self.best_acc = acc_mean
            print('Train-Epoch:%3d,  Loss: %.3f, Acc:%.3f' % (epoch+1, loss_mean, acc_mean))
        return self.best_acc


class RunModel(object):
    def do_work(self):
        best_acc = 0.0
        paddle.set_device("gpu:2")
        mod = TrainModel()
        best_acc = mod.train(5)
        print('Finshed! The best acc : %3f' % best_acc)


