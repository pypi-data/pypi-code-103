"""
Machine Learning Utilities
--------------------------
The ``maica.ml_old.util`` module provides essential functions for training configuration and model reuse.
Most deep learning algorithms in MAICA are based on this module.
"""

import numpy
import copy
import torch
import pandas
import os
import graphviz
import xgboost
import torch.utils.data as tdata
import torch_geometric.data as tgdata
from maica.core.env import *
from maica.core.sys import *
from maica.ml_old.base import Model
from sklearn.tree import export_graphviz
from maica.ml_old.base import SKLearnModel
from maica.data.base import Dataset
from maica.ml_old.nn import FCNN
from maica.ml_old.nn import Autoencoder


# def get_data_loader(*data: object,
#                     batch_size: int = 8,
#                     shuffle: bool = False):
#     """
#     Generate data_old loader object for a given dataset.
#     If the given data_old is ``numpy.ndarray``, it returns ``torch.DataLoader`` object.
#     If the data_old is ``maica_old.data_old.GraphDataset``, it returns ``torch_geometric.DataLoader`` object to iterate the graph-structured data_old.
#
#     :param data: (*object*) The dataset to be iterated by the data_old loader.
#     :param batch_size: (*int, optional*) The batch size of the data_old loader (*default* = 8).
#     :param shuffle: (*int, optional*) An option to randomly sample the data_old when the iterations of the data_old loader (*default* = ``False``).
#     :return: (*object*) Data loader object to load the dataset.
#     """
#
#     if isinstance(data[0], numpy.ndarray):
#         # Generate data_old loader for the vector dataset including the numerical vectors and the chemical formulas.
#         tensors = [torch.tensor(d, dtype=torch.float) for d in data]
#         return tdata.DataLoader(tdata.TensorDataset(*tuple(tensors)), batch_size=batch_size, shuffle=shuffle)
#     elif isinstance(data[0], GraphDataset):
#         # Generate data_old loader for the graph dataset including the numerical vectors and the chemical formulas.
#         return tgdata.DataLoader(data[0].data, batch_size=batch_size, shuffle=shuffle)
#     else:
#         raise AssertionError('The type of the given data_old object(s) is not valid.' +
#                              ' Only numpy.ndarray and ml_old.data_old.Dataset is acceptable for this function.')
#
#
# def get_batch_size(dataset: Dataset):
#     """
#     Return an appropriate batch size of the dataset.
#
#     :param dataset: (*maica.data_old.base.Dataset*) A dataset will be used served to the data_old loader object.
#     :return: (*int*) The batch size for the dataset.
#     """
#
#     if dataset.n_data > 4096:
#         return 128
#     elif dataset.n_data > 1024:
#         return 64
#     elif dataset.n_data > 512:
#         return 32
#     else:
#         return numpy.maximum(1, int(dataset.n_data / 10))
#
#
# def get_optimizer(model_params: torch.Generator,
#                   gd_name: str,
#                   init_lr: float = 1e-3,
#                   l2_reg: float = 1e-6):
#     """
#     Return a gradient descent optimizer to fit model parameters.
#
#     :param model_params: (*torch.Generator*) Model parameters to be trained by the generated optimizer.
#     :param gd_name: (*str*) A name of the gradient descent method to fit model parameters (defined in ``maica_old.core.env``).
#     :param init_lr: (*float, optional*) An initial learning rate of the gradient descent optimizer (*default* = 1e-3).
#     :param l2_reg: (*float, optional*) A coefficient of the L2 regularization in model parameters (*default* = 1e-6).
#     :return: (*torch.optim.Optimizer*) A gradient descent optimizer to fit the model parameters.
#     """
#
#     # Define the gradient descent method to optimize the model parameters.
#     if gd_name == GD_SGD:
#         optimizer = torch.optim.SGD(model_params, lr=init_lr, weight_decay=l2_reg, momentum=0.9)
#     elif gd_name == GD_ADADELTA:
#         optimizer = torch.optim.Adadelta(model_params, lr=init_lr, weight_decay=l2_reg)
#     elif gd_name == GD_RMSPROP:
#         optimizer = torch.optim.RMSprop(model_params, lr=init_lr, weight_decay=l2_reg)
#     elif gd_name == GD_ADAM:
#         optimizer = torch.optim.Adam(model_params, lr=init_lr, weight_decay=l2_reg)
#     else:
#         raise AssertionError('Unknown name of the gradient method {} was given.'.format(gd_name))
#
#     return optimizer
#
#
# def get_loss_func(loss_func: str):
#     """
#     Return a loss function to evaluate the model performance.
#
#     :param loss_func: (*str*) A name of the loss function to evaluate model performance (defined in `maica_old.core.env``).
#     :return: (*object*) A loss function object to evaluate the model performance.
#     """
#
#     # Define the loss function to evaluate the model performance.
#     if loss_func == LOSS_MAE:
#         criterion = torch.nn.L1Loss()
#     elif loss_func == LOSS_MSE:
#         criterion = torch.nn.MSELoss()
#     elif loss_func == LOSS_SMAE:
#         criterion = torch.nn.SmoothL1Loss()
#     else:
#         raise AssertionError('Unknown name of the loss function {} was given.'.format(loss_func))
#
#     return criterion


def get_model(alg_name: str,
              **kwargs):
    if alg_name in ALGS[SRC_SKLEARN]:
        # Scikit-learn Algorithms
        return SKLearnModel(alg_name, **kwargs)
    elif alg_name in ALGS[SRC_PYTORCH]:
        # Pytorch Algorithms
        if alg_name == ALG_FCNN:
            model = FCNN(dim_in=kwargs['dim_in'], dim_out=kwargs['dim_out'])
        elif alg_name == ALG_ATE:
            model = Autoencoder(dim_in=kwargs['dim_in'], dim_latent=kwargs['dim_latent'])
        # elif alg_name == env.ALG_GCN:
        #     readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
        #     n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
        #     model = GCN(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
        #                 readout=readout)
        # elif alg_name == env.ALG_GAT:
        #     readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
        #     n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
        #     model = GAT(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
        #                 readout=readout)
        # elif alg_name == env.ALG_GIN:
        #     readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
        #     n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
        #     model = GIN(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'], n_graphs=n_graphs,
        #                 readout=readout)
        # elif alg_name == env.ALG_CGCNN:
        #     readout = kwargs['readout'] if 'readout' in kwargs.keys() else 'mean'
        #     n_graphs = kwargs['n_graphs'] if 'n_graphs' in kwargs.keys() else 1
        #     model = CGCNN(n_node_feats=kwargs['n_node_feats'], n_edge_feats=kwargs['n_edge_feats'],
        #                   dim_out=kwargs['dim_out'], n_graphs=n_graphs, readout=readout)
        # else:
        #     raise AssertionError('Invalid request received with unknown algorithm name: {}.'.format(alg_name))

        # Move model parameters from CPU to GPU when sys.run_gpu is enabled.
        if is_gpu_runnable():
            model.gpu()

        return model


# def save_pred_results(task_name: str,
#                       model: Model,
#                       dataset_test: Dataset,
#                       preds: numpy.ndarray):
#     """
#     Save the model parameters and the prediction results as a model file and an excel file.
#
#     :param task_name: (*str*) A name of your task.
#     :param model: (*ml_old.base.Model)* A model used will be evaluated.
#     :param dataset_test: (*data_old.base.Dataset*) A dataset used to the evaluation.
#     :param preds: (*numpy.ndarray*) Prediction results of the model for the dataset.
#     """
#
#     # Make a directory to save the evaluation results.
#     if not os.path.exists(task_name):
#         os.mkdir(task_name)
#
#     # Save the trained model.
#     if model.alg_name in ALGS[PIP_JOBLIB]:
#         model.save(task_name + '/model_' + model.alg_name + '.joblib')
#     elif model.alg_name in ALGS[PIP_PYTORCH]:
#         model.save(task_name + '/model_' + model.alg_name + '.pt')
#     else:
#         raise AssertionError('Unknown algorithm type: {}.'.format(model.alg_type))
#
#     # Save the prediction results.
#     idx_data = dataset_test.idx_data.reshape(-1, 1)
#     targets = dataset_test.y.reshape(-1, 1)
#     _preds = preds.reshape(-1, 1)
#     df = pandas.DataFrame(numpy.hstack([idx_data, targets, _preds]))
#     df.to_excel(task_name + '/pred_results_' + model.alg_name + '.xlsx',
#                 index=None, header=['data_index', 'target', 'prediction'])
