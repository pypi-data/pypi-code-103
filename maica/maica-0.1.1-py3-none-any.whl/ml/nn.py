"""
Neural Networks
---------------
The ``maica.ml_old.nn`` module provides an implementation of the most essential feedforward neural network.
The algorithms in this module are used to predict target values from the feature vectors and the chemical formulas.
"""


import numpy
import torch
import torch.nn as nn
import torch.nn.functional as F
import maica.core.sys as sys
import maica.core.env as env
from maica.ml_old.base import PyTorchModel


class FCNN(PyTorchModel):
    """
    Fully-connected neural network with the three hidden layers and the one output layer.
    For each hidden layer, the batch normalization technique is applied to accelerate the model training.
    """

    def __init__(self,
                 dim_in: int,
                 dim_out: int):
        super(FCNN, self).__init__(env.ALG_FCNN)
        self.fc1 = nn.Linear(dim_in, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.fc2 = nn.Linear(256, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.fc3 = nn.Linear(256, 32)
        self.bn3 = nn.BatchNorm1d(32)
        self.fc4 = nn.Linear(32, dim_out)

    def forward(self,
                x: torch.tensor):
        """
        Predict target values for the given data_old ``x``.

        :param x: (*torch.tensor*) A tensor containing input data_old of the model.
        :return: (*torch.Tensor*) Predicted values.
        """

        h = F.relu(self.bn1(self.fc1(x)))
        h = F.relu(self.bn2(self.fc2(h)))
        h = F.relu(self.bn3(self.fc3(h)))
        out = self.fc4(h)

        return out

    def fit(self,
            data_loader: torch.utils.data.DataLoader,
            optimizer: torch.optim.Optimizer,
            criterion: object):
        """
        Fit the model parameters for the given dataset using the data_old loader, the optimizer, and the loss function.
        It iterates the parameter optimization once for the entire dataset.

        :param data_loader: (*torch.utils.data_old.DataLoader*) A data_old loader to sample the data_old from the training dataset.
        :param optimizer: (*torch.optim.Optimizer*) An optimizer to fit the model parameters.
        :param criterion: (*object*) A loss function to evaluate the prediction performance of the model.
        :return: (*float*) Training loss.
        """

        self.train()
        sum_losses = 0

        for data, targets in data_loader:
            if sys.run_gpu:
                data = data.cuda()
                targets = targets.cuda()

            preds = self(data)
            loss = criterion(preds, targets.reshape(-1, 1))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sum_losses += loss.item()

        return sum_losses / len(data_loader)

    def predict(self,
                data_loader: object):
        """
        Predict target values for the given dataset in the data_old loader.

        :param data_loader: (*torch.utils.data_old.DataLoader*) A data_old loader to sample the data_old from the dataset.
        :return: (*numpy.ndarray*) Predicted values.
        """

        self.eval()
        list_preds = list()

        with torch.no_grad():
            for data in data_loader:
                if sys.run_gpu:
                    list_preds.append(self(data[0].cuda()).cpu().numpy())
                else:
                    list_preds.append(self(data[0]).numpy())

        return numpy.vstack(list_preds).flatten()


class Autoencoder(PyTorchModel):
    """
    A neural network to generate latent embeddings of input data_old.
    It is trained to minimize the difference between the input and its output rather than to be trained based on the target values.
    The training problem of the autoencoder can be defined by:

    .. math::
        \theta^* = \argmin_{\theta} ||\mathbf{x} - \mathbf{x}^{'}||_2^2,

    where :math:`mathbf{x}` is the input data_old, and :math:`\mathbf{x}^{'}` is the predicted value of the autoencoder.
    """

    def __init__(self,
                 dim_in: int,
                 dim_latent: int):
        super(Autoencoder, self).__init__(env.ALG_ATE)
        self.enc_fc1 = nn.Linear(dim_in, 256)
        self.enc_fc2 = nn.Linear(256, dim_latent)
        self.dec_fc1 = nn.Linear(dim_latent, 256)
        self.dec_fc2 = nn.Linear(256, dim_in)

    def forward(self,
                x: torch.tensor):
        """
        Perform encoding and decoding for the given data_old ``x``.

        :param x: (*torch.tensor*) The input data_old of the model.
        :return: The decoded input.
        """

        z = self.enc(x)
        x_p = self.dec(z)

        return x_p

    def enc(self,
            x: torch.tensor):
        """
        Generate the latent embedding of the input data_old ``x``.
        This is called :obj:`encoding` in the autoencoders.

        :param x: (*torch.tensor*) The input data_old of the model.
        :return: Latent embedding of the input data_old ``x``.
        """

        h = F.leaky_relu(self.enc_fc1(x))
        z = F.leaky_relu(self.enc_fc2(h))

        return z

    def dec(self,
            z: torch.tensor):
        """
        Restore the input data_old from the latent embedding of the input data_old.
        This is called :obj:`decoding` in the autoencoders.

        :param z: (*torch.tensor*) The latent embedding.
        :return: Restored input data_old from the given latent embedding ``z``.
        """

        h = F.leaky_relu(self.dec_fc1(z))
        x_p = self.dec_fc2(h)

        return x_p

    def fit(self,
            data_loader: torch.utils.data.DataLoader,
            optimizer: torch.optim.Optimizer):
        """
        Fit the model parameters for the given dataset using the data_old loader and the optimizer.
        It iterates the parameter optimization once for the entire dataset.

        :param data_loader: (*torch.utils.data_old.DataLoader*) A data_old loader to sample the data_old from the training dataset.
        :param optimizer: (*torch.optim.Optimizer*) An optimizer to fit the model parameters.
        :return: Training loss.
        """

        self.train()
        sum_losses = 0

        for data in data_loader:
            data = data[0]

            if sys.run_gpu:
                data = data.cuda()

            preds = self(data)
            loss = torch.mean((data - preds)**2)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            sum_losses += loss.item()

        return sum_losses / len(data_loader)

    def predict(self,
                data_loader: object):
        """
        Predict target values for the given dataset in the data_old loader.

        :param data_loader: (*torch.utils.data_old.DataLoader*) A data_old loader to sample the data_old from the dataset.
        :return: A NumPy array containing the predicted values.
        """

        self.eval()
        list_preds = list()

        with torch.no_grad():
            for data in data_loader:
                if sys.run_gpu:
                    list_preds.append(self.enc(data.cuda()).cpu().numpy())
                else:
                    list_preds.append(self.enc(data).numpy())

        return numpy.vstack(list_preds)
