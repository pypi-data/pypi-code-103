import torch
import torch.nn as nn

from actnn.layers import QLinear, QReLU, QBatchNorm1d, QDropout

from cogdl.utils import spmm, get_activation


class ActMul(torch.autograd.Function):
    @staticmethod
    def forward(self, x, c):
        self.c = c
        return x * c

    @staticmethod
    def backward(self, grad_output):
        grad_input = grad_output.clone()
        grad_input *= self.c
        return grad_input, None

def act_mul(x, c):
    return ActMul.apply(x, c)

class ActGINLayer(nn.Module):
    r"""Graph Isomorphism Network layer from paper `"How Powerful are Graph
    Neural Networks?" <https://arxiv.org/pdf/1810.00826.pdf>`__.

    .. math::
        h_i^{(l+1)} = f_\Theta \left((1 + \epsilon) h_i^{l} +
        \mathrm{sum}\left(\left\{h_j^{l}, j\in\mathcal{N}(i)
        \right\}\right)\right)

    Parameters
    ----------
    apply_func : callable layer function)
        layer or function applied to update node feature
    eps : float32, optional
        Initial `\epsilon` value.
    train_eps : bool, optional
        If True, `\epsilon` will be a learnable parameter.
    """

    def __init__(self, in_features, out_features, pooled_features, apply_func=None, eps=0, train_eps=True, dropout=0.0, activation="relu", norm=None):
        super(ActGINLayer, self).__init__()
        if train_eps:
            self.eps = torch.nn.Parameter(torch.FloatTensor([eps]))
        else:
            self.register_buffer("eps", torch.FloatTensor([eps]))
        self.apply_func = apply_func
        # self.linear = QLinear(in_features, out_features)
        self.linear_prediction = QLinear(out_features, pooled_features)
        if dropout > 0:
            self.dropout = QDropout(dropout)
        else:
            self.dropout = None
        if activation is not None:
            self.act = QReLU()
        else:
            self.act = None

        if norm is not None:
            if norm == "batchnorm":
                self.norm = QBatchNorm1d(out_features)
            else:
                raise NotImplementedError
        else:
            self.norm = None

    def forward(self, graph, x):
        out = (1 + self.eps) * x + spmm(graph, x, actnn=True)
        if self.apply_func is not None:
            out = self.apply_func(out)
        # out = self.linear(out)

        if self.norm is not None:
            out = self.norm(out)
        if self.act is not None:
            out = self.act(out)

        # if self.dropout is not None:
        #     out = self.dropout(out)

        device = x.device
        batchsize = int(torch.max(graph.batch)) + 1

        pooled = self.linear_prediction(out)
        hsize = pooled.shape[1]
        pooled2 = torch.zeros(batchsize, hsize).to(device)
        pooled2.scatter_add_(dim=0, index=graph.batch.view(-1, 1).repeat(1, hsize), src=pooled)
        if self.dropout is not None:
            pooled2 = self.dropout(pooled2)

        return out, pooled2
