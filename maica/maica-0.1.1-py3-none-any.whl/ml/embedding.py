import torch
import torch.nn as nn
import torch.nn.functional as F
from maica.core.env import *
from maica.ml.base import PyTorchModel
from maica.core.sys import is_gpu_runnable


class Autoencoder(PyTorchModel):
    """
    A neural network to generate latent embeddings of input data_old.
    It is trained to minimize the difference between the input and its output rather than to be trained based on the target values.
    The training problem of the autoencoder can be defined by:

    .. math::
        \theta^* = \argmin_{\theta} ||\mathbf{x} - \mathbf{x}^{'}||_2^2,

    where :math:`mathbf{x}` is the input data, and :math:`\mathbf{x}^{'}` is the predicted value of the autoencoder.
    """

    def __init__(self,
                 dim_in: int,
                 dim_latent: int):
        super(Autoencoder, self).__init__(ALG_ATE)
        self.enc_fc1 = nn.Linear(dim_in, 256)
        self.enc_fc2 = nn.Linear(256, dim_latent)
        self.dec_fc1 = nn.Linear(dim_latent, 256)
        self.dec_fc2 = nn.Linear(256, dim_in)

    def forward(self,
                x: torch.tensor):
        """
        Perform encoding and decoding for given data_old ``x``.

        :param x: (*torch.Tensor*) Input data_old of the model.
        :return: (*torch.Tensor*) The reconstructed input.
        """

        z = self.enc(x)
        x_p = self.dec(z)

        return x_p

    def enc(self,
            x: torch.tensor):
        """
        Generate the latent embedding of input data_old ``x``.
        This is called :obj:`encoding` in the autoencoders.

        :param x: (*torch.Tensor*) Input data_old of the model.
        :return: (*torch.Tensor*) Latent embedding of the input data_old ``x``.
        """

        h = F.leaky_relu(self.enc_fc1(x))
        z = F.leaky_relu(self.enc_fc2(h))

        return z

    def dec(self,
            z: torch.tensor):
        """
        Restore the input data_old from the latent embedding of the input data_old.
        This is called :obj:`decoding` in the autoencoders.

        :param z: (*torch.Tensor*) The latent embedding.
        :return: (*torch.Tensor*) Reconstructed input data_old from the given latent embedding ``z``.
        """

        h = F.leaky_relu(self.dec_fc1(z))
        x_p = self.dec_fc2(h)

        return x_p

    def fit(self,
            data_loader: torch.utils.data.DataLoader,
            optimizer: torch.optim.Optimizer,
            criterion: object):
        """
        Fit the model parameters for the given dataset using the data_old loader and the optimizer.
        It iterates the parameter optimization once for the entire dataset.

        :param data_loader: (*torch.utils.data_old.DataLoader*) A data_old loader to sample the data_old from the training dataset.
        :param optimizer: (*torch.optim.Optimizer*) An optimizer to fit the model parameters.
        :param criterion: (*object*) A loss function to evaluate the prediction performance of the model.
        :return: (*float*) Reconstruction loss.
        """

        self.train()
        sum_losses = 0

        for data in data_loader:
            data = data[0]

            if is_gpu_runnable():
                data = data.cuda()

            preds = self(data)
            loss = criterion(data, preds)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sum_losses += loss.item()

        return sum_losses / len(data_loader)

    def predict(self,
                data: object):
        self.eval()

        with torch.no_grad():
            __data = torch.tensor(data, dtype=torch.float)

            if is_gpu_runnable():
                return self.enc(__data.cuda()).cpu().numpy()
            else:
                return self.enc(__data).numpy()
