"""
Feedforward Neural Networks
---------------------------
The ``maica.ml.fnn`` module provides an implementation of the most essential feedforward neural network.
The algorithms in this module are used to predict target values from the feature vectors and the chemical formulas.
"""


import torch.utils.data
import torch.nn as nn
import torch.nn.functional as F
from abc import abstractmethod
from maica.core.env import *
from maica.core.sys import *
from maica.ml.base import PyTorchModel
from maica.ml.embedding import Autoencoder


class FNN(PyTorchModel):
    @abstractmethod
    def __init__(self,
                 alg_name: str):
        super(FNN, self).__init__(alg_name)

    @abstractmethod
    def forward(self,
                data: object):
        pass

    def fit(self,
            data_loader: object,
            optimizer: torch.optim.Optimizer,
            criterion: object):
        self.train()
        train_loss = 0

        for data, targets in data_loader:
            if is_gpu_runnable():
                data = data.cuda()
                targets = targets.cuda()

            preds = self(data)
            loss = criterion(preds, targets)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        return train_loss / len(data_loader)

    def predict(self,
                data: object):
        self.eval()

        with torch.no_grad():
            __data = torch.tensor(data, dtype=torch.float)

            if is_gpu_runnable():
                return self(__data.cuda()).cpu().numpy()
            else:
                return self(__data).numpy()


class FCNN(FNN):
    def __init__(self,
                 dim_in: int,
                 dim_out: int):
        super(FCNN, self).__init__(ALG_FCNN)
        self.fc1 = nn.Linear(dim_in, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.fc2 = nn.Linear(256, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.fc3 = nn.Linear(256, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.fc4 = nn.Linear(32, dim_out)

    def forward(self,
                x: torch.tensor):
        h = F.relu(self.bn1(self.fc1(x)))
        h = F.relu(self.bn2(self.fc2(h)))
        h = F.relu(self.bn3(self.fc3(h)))
        out = self.fc4(h)

        return out


class DopNet(FNN):
    def __init__(self,
                 dim_in_host: int,
                 dim_in_dop: int,
                 dim_host_emb: int,
                 dim_out: int):
        super(DopNet, self).__init__(ALG_DOPNET)
        self.dim_in_host = dim_in_host
        self.emb_net = Autoencoder(dim_in=dim_in_host, dim_latent=dim_host_emb)
        self.pred_net = FCNN(dim_in=dim_host_emb+dim_in_dop, dim_out=dim_out)

    def forward(self,
                x: torch.tensor):
        host_embs = self.emb_net.enc(x[:, :self.dim_in_host])
        out = self.pred_net(torch.cat([host_embs, x[:, self.dim_in_host:]], dim=1))

        return out
