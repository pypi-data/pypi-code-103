import torch


class BaseLoss(torch.nn.Module):
    def __init__(self):
        super(BaseLoss, self).__init__()

    def forward(self, *args):
        raise NotImplementedError
