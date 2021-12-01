import torch
import torch.nn as nn
import math
from cogdl.layers import AutoLayer
from cogdl.utils import get_activation

from .. import BaseModel


class AutoGNN(BaseModel):

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
        parser.add_argument("--lambda", dest="lmbda", type=float, default=0.5)
        parser.add_argument("--alpha", type=float, default=0.1)
        parser.add_argument("--wd1", type=float, default=5e-4)
        parser.add_argument("--wd2", type=float, default=5e-4)
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
            args.alpha,
            args.lmbda,
            args.wd1,
            args.wd2,
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
        alpha=0.1,
        lmbda=0.5,
        wd1=5e-4,
        wd2=5e-4,
    ):
        super(AutoGNN, self).__init__()
        self.num_layers = num_layers
        self.alpha = alpha
        self.lmbda = lmbda
        self.wd1 = wd1
        self.wd2 = wd2

        self.layers = nn.ModuleList(
            [
                AutoLayer(
                    hidden_size,
                    hidden_size,
                    dropout=dropout,
                    residual=residual,
                    norm=norm,
                    activation=activation,
                    rp_ratio=rp_ratio,
                    alpha=alpha,
                    beta=math.log(self.lmbda / (i + 1) + 1),
                )
                for i in range(num_layers)
            ]
        )

        self.dropout = nn.Dropout(dropout)
        self.activation = get_activation(norm)

        self.fc_layers = nn.ModuleList()
        self.fc_layers.append(nn.Linear(in_feats, hidden_size))
        self.fc_layers.append(nn.Linear(hidden_size, out_feats))

        self.fc_parameters = list(self.fc_layers.parameters())
        self.conv_parameters = list(self.layers.parameters())

    def forward(self, graph):
        graph.sym_norm()
        x = graph.x
        h_init = self.dropout(x)
        h_init = self.activation(self.fc_layers[0](h_init))
        h = h_init

        for layer in self.layers:
            h = layer(graph, h, h_init)
        out = self.fc_layers[1](h)
        return out

    def get_optimizer(self, args):
        return torch.optim.Adam(
            [
                {"params": self.fc_parameters, "weight_decay": self.wd1},
                {"params": self.conv_parameters, "weight_decay": self.wd2},
            ],
            lr=args.lr,
        )
