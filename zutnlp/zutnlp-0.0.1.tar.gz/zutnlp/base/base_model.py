import torch


class BaseModel(torch.nn.Module):

    def __init__(self):
        super(BaseModel, self).__init__()

    def predict(self, *args, **kwargs):
        raise NotImplementedError
