import torch
import torch.nn as nn
from cogdl.layers import FGCNLayer

from .. import BaseModel


class FGCN(BaseModel):

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
        parser.add_argument("--sample-size", type=int, default=2)
        parser.add_argument("--sample-ratio", type=float, default=0.5)
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
            args.sample_ratio,
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
        sample_size=2,
        sample_ratio=0.5,
    ):
        super(FGCN, self).__init__()
        self.hist = []
        self.first_epoch = True
        self.sample_size = sample_size
        self.sample_ratio = sample_ratio
        self.hidden_size = hidden_size
        self.in_feats = in_feats
        self.out_feats = out_feats
        # self.fc_layers = nn.ModuleList()
        # self.fc_layers.append(nn.Linear(in_feats, hidden_size))
        # self.fc_layers.append(nn.Linear(hidden_size, out_feats))

        shapes = [in_feats] + [hidden_size] * (num_layers - 1) + [out_feats]
        Layer = FGCNLayer
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
        self.dropout = nn.Dropout(p=dropout)
        self.activation = nn.ReLU()

        self.first_epoch = False
        self.hist = [None for _ in range(self.num_layers)]


    def forward(self, graph):
        graph.sym_norm()
        h = graph.x
        # h = self.dropout(h)
        # h = self.activation(self.fc_layers[0](h))
        if not self.training:
            for i in range(self.num_layers):
                h = self.layers[i](graph, h)
            return h
        if self.first_epoch:
            for i in range(self.num_layers):
                self.hist[i] = h.detach()
                h = self.layers[i](graph, h)
            self.first_epoch = False
            return h
        for i in range(self.num_layers):
            if i > 0:
                # idx = torch.randint(self.hidden_size, (self.hidden_size // self.sample_size, )).to(h.device)
                idx = torch.randint(self.hidden_size, (int(self.hidden_size * self.sample_ratio), )).to(h.device)
                h = self.layers[i](graph, h, idx, self.sample_size, self.hist[i])
            else:
                # idx = torch.randint(self.in_feats, (self.in_feats // self.sample_size, )).to(h.device)
                idx = torch.randint(self.in_feats, (int(self.in_feats * self.sample_ratio), )).to(h.device)
                h = self.layers[i](graph, h, idx, self.sample_size, self.hist[i])
        # h = self.fc_layers[1](h)
        return h

    def predict(self, data):
        return self.forward(data)
