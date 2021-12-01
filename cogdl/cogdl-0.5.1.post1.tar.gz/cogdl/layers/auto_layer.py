import math

import torch
import torch.nn as nn

from cogdl.utils import spmm, get_activation


# def propagation(graph, x, type="gcn"):
#     hidden = spmm(graph, x)

#     row, col = graph.edge_index
#     # Self-attention on the nodes - Shared attention mechanism
#     h_l = (self.a_l * h).sum(dim=-1)
#     h_r = (self.a_r * h).sum(dim=-1)

#     if self.dropout.p == 0.0 and graph.is_symmetric() and check_fused_gat():
#         out = fused_gat_op(h_l, h_r, graph, self.alpha, h)
#         out = out.view(out.shape[0], -1)
#     else:
#         # edge_attention: E * H
#         edge_attention = self.leakyrelu(h_l[row] + h_r[col])
#         edge_attention = edge_softmax(graph, edge_attention)
#         edge_attention = self.dropout(edge_attention)

#         if check_mh_spmm() and next(self.parameters()).device.type != "cpu":
#             if self.nhead > 1:
#                 h_prime = mh_spmm(graph, edge_attention, h)
#                 out = h_prime.view(h_prime.shape[0], -1)
#             else:
#                 edge_weight = edge_attention.view(-1)
#                 with graph.local_graph():
#                     graph.edge_weight = edge_weight
#                     out = spmm(graph, h.squeeze(1))
#         else:
#             with graph.local_graph():
#                 h_prime = []
#                 h = h.permute(1, 0, 2).contiguous()
#                 for i in range(self.nhead):
#                     edge_weight = edge_attention[:, i]
#                     graph.edge_weight = edge_weight
#                     hidden = h[i]
#                     assert not torch.isnan(hidden).any()
#                     h_prime.append(spmm(graph, hidden))
#             out = torch.cat(h_prime, dim=1)


class AutoLayer(nn.Module):

    def __init__(
        self, in_features, out_features, dropout=0.0, activation=None, residual=False, norm=None, bias=True, alpha=0.1, beta=1, **kwargs
    ):
        super(AutoLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.alpha = alpha
        self.beta = beta
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

    def forward(self, graph, x, init_x):
        hidden = spmm(graph, x)
        hidden = (1 - self.alpha) * hidden + self.alpha * init_x
        out = self.beta * self.linear(hidden) + (1 - self.beta) * hidden

        if self.norm is not None:
            out = self.norm(out)
        if self.act is not None:
            out = self.act(out)

        if self.residual is not None:
            out = out + self.residual(x)
        if self.dropout is not None:
            out = self.dropout(out)
        return out
