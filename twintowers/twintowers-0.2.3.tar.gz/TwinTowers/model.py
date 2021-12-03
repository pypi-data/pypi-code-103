import torch
from . import esm
from .PretrainedModels.config import load_model_architecture
from torch.nn.functional import gelu


class MSARetrieveModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.esm1b = load_model_architecture(name="esm-1b")

        # 去掉不用的参数的梯度
        for param in self.esm1b.lm_head.parameters():
            param.requires_grad = False
        for param in self.esm1b.contact_head.parameters():
            param.requires_grad = False
            
        self.layer = self.esm1b.num_layers
        self.dim = self.esm1b.args.embed_dim

    def forward(self, inputs, lengths=None, use_checkpoint=False):
        outputs = self.esm1b(inputs, repr_layers=[self.layer], use_checkpoint=use_checkpoint)

        if lengths:
            outputs = outputs["representations"][self.layer]
            vec_out = outputs[0, 1: lengths[0]+1].mean(dim=0, keepdim=True)
            for i, l in enumerate(lengths[1:]):
                vec = outputs[i+1, 1: l+1].mean(dim=0, keepdim=True)
                vec_out = torch.cat((vec_out, vec), dim=0)

        else:
            vec_out = outputs["representations"][self.layer][:, 0, :]

        out_dict = {'repr': vec_out}

        return out_dict


class ThresholdModel(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc1 = torch.nn.Linear(dim, dim * 2)
        self.fc2 = torch.nn.Linear(dim * 2, dim * 2)
        self.out = torch.nn.Linear(dim * 2, 1)

    def forward(self, inputs):
        x1 = gelu(self.fc1(inputs))
        x2 = gelu(self.fc2(x1))
        t = gelu(self.out(x2)).squeeze(-1)
        return t


if __name__ == '__main__':
    model = MSARetrieveModel()
    print(model)
