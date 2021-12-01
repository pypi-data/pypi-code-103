import numpy as np
import torch
import torch.nn as nn
from cogdl.layers import FSGCNLayer
from cogdl.utils import spmm

from .. import BaseModel


class FSGCN(BaseModel):

    @staticmethod
    def add_args(parser):
        """Add model-specific arguments to the parser."""
        # fmt: off
        parser.add_argument("--num-features", type=int)
        parser.add_argument("--num-classes", type=int)
        parser.add_argument("--num-layers", type=int, default=2)
        parser.add_argument("--hidden-size", type=int, default=64)
        parser.add_argument("--dropout", type=float, default=0.5)
        parser.add_argument("--residual", action="store_true")
        parser.add_argument("--norm", type=str, default=None)
        parser.add_argument("--activation", type=str, default="relu")
        parser.add_argument("--sample-size", type=int, default=[2], nargs="+", metavar="N")
        # fmt: on

    @classmethod
    def build_model_from_args(cls, args):
        return cls(
            args.num_features,
            args.hidden_size,
            args.num_classes,
            args.num_layers,
            args.dropout,
            args.activation,
            args.residual,
            args.norm,
            args.actnn,
            args.rp_ratio,
            args.sample_size,
        )

    def __init__(
        self,
        in_feats,
        hidden_size,
        out_feats,
        num_layers,
        dropout,
        activation="relu",
        residual=False,
        norm=None,
        actnn=False,
        rp_ratio=1,
        sample_size=[2],
    ):
        super(FSGCN, self).__init__()
        self.hist = []
        self.first_epoch = True
        if len(sample_size) == 1:
            self.sample_size = sample_size * (num_layers - 1)
        self.hidden_size = hidden_size
        self.out_feats = out_feats
        shapes = [in_feats] + [hidden_size] * (num_layers - 1) + [out_feats]
        Layer = FSGCNLayer
        self.layers = nn.ModuleList(
            [
                Layer(
                    shapes[i],
                    shapes[i + 1],
                    dropout=dropout if i != num_layers - 1 else 0,
                    residual=residual if i != num_layers - 1 else None,
                    norm=norm if i != num_layers - 1 else None,
                    activation=activation if i != num_layers - 1 else None,
                    rp_ratio=rp_ratio,
                )
                for i in range(num_layers)
            ]
        )
        self.num_layers = num_layers

    def forward(self, graph):
        graph.sym_norm()
        h = graph.x
        if not self.training:
            # self.hist = []
            for i in range(self.num_layers):
                # self.hist.append(spmm(graph, h))
                h = self.layers[i](graph, h)
            return h
        # with torch.no_grad():
        #     self.hist = []
        #     for i in range(self.num_layers):
        #         self.hist.append(spmm(graph, h.detach()))
        #         h = self.layers[i](graph, h)
        if self.first_epoch:
            for i in range(self.num_layers):
                self.hist.append(spmm(graph, h.detach()))
                h = self.layers[i](graph, h)
            self.first_epoch = False
        else:
            idx = torch.randint(self.hidden_size, (self.sample_size[0],)).to(h.device)
            # if np.random.random() < 0.5:
            #     idx = torch.arange(self.hidden_size // 2).to(h.device)
            # else:
            #     idx = torch.arange(start=self.hidden_size // 2, end = self.hidden_size).to(h.device)
            out_idx = torch.arange(self.out_feats).to(h.device)
            for i in range(self.num_layers):
                # cur_idx = torch.randint(self.hidden_size, (self.sample_size[i],)).to(h.device) if i < self.num_layers - 1 else out_idx
                cur_idx = idx if i < self.num_layers - 1 else out_idx
                if i > 0:
                    h = self.layers[i](graph, h, self.hist[i], idx, cur_idx)
                else:
                    h = self.layers[i](graph, h, self.hist[i], None, cur_idx)
                # if i < self.num_layers - 1:
                #     h = spmm(graph, h)
                #     self.hist[i + 1][:, cur_idx] = h.detach()
                    # with torch.no_grad():
                    #     self.hist[i + 1][:, cur_idx] = spmm(graph, h.detach())
                idx = cur_idx
        return h

    def predict(self, data):
        return self.forward(data)
