import math

import torch
import torch.nn as nn

from cogdl.utils import spmm, get_activation


class FSGCNLayer(nn.Module):

    def __init__(
        self, in_features, out_features, dropout=0.0, activation=None, residual=False, norm=None, bias=True, **kwargs
    ):
        super(FSGCNLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        if dropout > 0:
            self.dropout = nn.Dropout(dropout)
        else:
            self.dropout = None
        if residual:
            self.residual = nn.Linear(in_features, out_features)
        else:
            self.residual = None

        if activation is not None:
            self.act = get_activation(activation, inplace=True)
        else:
            self.act = None

        if norm is not None:
            if norm == "batchnorm":
                self.norm = nn.BatchNorm1d(out_features)
            elif norm == "layernorm":
                self.norm = nn.LayerNorm(out_features)
            else:
                raise NotImplementedError
        else:
            self.norm = None

        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1.0 / math.sqrt(self.out_features)
        torch.nn.init.uniform_(self.linear.weight, -stdv, stdv)

    def forward(self, graph, x, hx=None, idx=None, cur_idx=None):
        if cur_idx is not None:
            if idx is not None:
                out = hx.detach()
                out[:, idx] = spmm(graph, x)
                # out = spmm_with_replace(graph, x, hx.detach(), idx)
                # t1 = self.linear(out)[:, cur_idx]
                # tmp = spmm(graph, x) - out[:, idx]
                # t2 = torch.addmm(self.linear.bias[cur_idx], tmp, self.linear.weight[cur_idx, :][:, idx].t())
                # out = t1 + t2
            else:
                out = hx
            out = torch.addmm(self.linear.bias[cur_idx], out, self.linear.weight[cur_idx, :].t())
        else:
            out = self.linear(x)
            out = spmm(graph, out)

        if self.norm is not None:
            out = self.norm(out)
        if self.act is not None:
            out = self.act(out)

        if self.residual is not None:
            out = out + self.residual(x)
        if self.dropout is not None:
            out = self.dropout(out)

        return out
