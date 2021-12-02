"""
Graph Neural Networks
---------------------
The ``maica.ml.gnn`` module provides an implementation of the most essential feedforward neural network.
The algorithms in this module are used to predict target values from the feature vectors and the chemical formulas.
"""


import torch.utils.data
import torch.nn as nn
import torch.nn.functional as F
from abc import abstractmethod
from torch_geometric.data import Batch
from torch_geometric.nn import GCNConv
from torch_geometric.nn import LayerNorm
from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import global_add_pool
from maica.core.env import *
from maica.core.sys import *
from maica.ml.base import PyTorchModel
from maica.ml.embedding import Autoencoder


class GNN(PyTorchModel):
    @abstractmethod
    def __init__(self,
                 alg_name: str):
        super(GNN, self).__init__(alg_name)

    @abstractmethod
    def _emb_node(self,
                  g: Batch):
        pass

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

        for batch in data_loader:
            if run_gpu:
                for b in batch:
                    b.x = b.x.cuda()
                    b.y = b.y.cuda()
                    b.edge_index = b.edge_index.cuda()
                    b.batch = b.batch.cuda()
                    b.edge_attr = None if b.edge_attr is None else b.edge_attr.cuda()

            preds = self(batch)
            loss = criterion(batch[0].y, preds)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.detach().item()

        return train_loss / len(data_loader)


class GCN(GNN):
    @abstractmethod
    def __init__(self,
                 n_node_feats: int,
                 dim_out: int,
                 readout: str = READOUT_MEAN):
        super(GNN, self).__init__(ALG_GCN)
        self.readout = readout
        self.gc1 = GCNConv(n_node_feats, 256)
        self.gn1 = LayerNorm(256)
        self.gc2 = GCNConv(256, 256)
        self.gn2 = LayerNorm(256)
        self.gc3 = GCNConv(256, 256)
        self.gn3 = LayerNorm(256)
        self.fc1 = nn.Linear(self.n_graphs * 256, 32)
        self.fc2 = nn.Linear(32, dim_out)

    def _emb_node(self,
                  g: Batch):
        h = F.relu(self.gn1(self.gc1(g.x, g.edge_index)))
        h = F.relu(self.gn2(self.gc2(h, g.edge_index)))
        h = F.relu(self.gn3(self.gc3(h, g.edge_index)))

        return h

    def forward(self,
                data: object):
        if self.readout == READOUT_MEAN:
            hg = torch.cat([global_mean_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)
        elif self.readout == READOUT_SUM:
            hg = torch.cat([global_add_pool(self.__emb_nodes(b), b.batch) for b in g], dim=1)

        hg = F.relu(self.fc1(hg))
        out = self.fc2(hg)

        return out
