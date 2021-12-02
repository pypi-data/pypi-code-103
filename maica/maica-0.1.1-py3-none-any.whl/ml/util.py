import numpy
import torch
import torch.utils.data as tdata
import torch_geometric.data as tgdata
from maica.core.env import *
from maica.ml.base import *
from maica.ml.fnn import *
from maica.ml.embedding import *
from maica.ml.gnn import *
from maica.core.sys import is_gpu_runnable
from maica.data.base import Dataset
from maica.data.base import GraphDataset


def get_model(alg_name: str,
              **kwargs):
    if alg_name in ALGS_SKLEARN:
        # Scikit-learn Algorithms
        return SKLearnModel(alg_name, **kwargs)
    elif alg_name in ALGS_PYTORCH:
        # Pytorch Algorithms
        if alg_name == ALG_FCNN:
            model = FCNN(dim_in=kwargs['dim_in'], dim_out=kwargs['dim_out'])
        elif alg_name == ALG_DOPNET:
            model = DopNet(dim_in_host=kwargs['dim_in_host'], dim_in_dop=kwargs['dim_in_dop'],
                           dim_host_emb=kwargs['dim_host_emb'], dim_out=kwargs['dim_out'])
        elif alg_name == ALG_ATE:
            model = Autoencoder(dim_in=kwargs['dim_in'], dim_latent=kwargs['dim_latent'])
        elif alg_name == ALG_GCN:
            model = GCN(n_node_feats=kwargs['n_node_feats'], dim_out=kwargs['dim_out'])

        if is_gpu_runnable():
            model.cuda()

        return model
    else:
        raise AssertionError('Undefined algorithm {} was given. Check available algorithms in \'maica.core.env\' file.'
                             .format(alg_name))


def get_data_loader(dataset: Dataset,
                    batch_size: int = 8,
                    shuffle: bool = False):
    if isinstance(dataset, GraphDataset):
        return tgdata.DataLoader([d.x for d in dataset.data], batch_size=batch_size, shuffle=shuffle)
    else:
        dataset.to_tensor()

        if dataset.contain_target:
            tensors = [dataset.x, dataset.y]
        else:
            tensors = [dataset.x]

        return tdata.DataLoader(tdata.TensorDataset(*tuple(tensors)), batch_size=batch_size, shuffle=shuffle)


def get_optimizer(model_params: torch.Generator,
                  gd_name: str,
                  init_lr: float = 1e-3,
                  l2_reg: float = 1e-6):
    if gd_name == GD_SGD:
        return torch.optim.SGD(model_params, lr=init_lr, weight_decay=l2_reg, momentum=0.9)
    elif gd_name == GD_ADADELTA:
        return torch.optim.Adadelta(model_params, lr=init_lr, weight_decay=l2_reg)
    elif gd_name == GD_RMSPROP:
        return torch.optim.RMSprop(model_params, lr=init_lr, weight_decay=l2_reg)
    elif gd_name == GD_ADAM:
        return torch.optim.Adam(model_params, lr=init_lr, weight_decay=l2_reg)
    else:
        raise AssertionError('Unknown gradient method {} was given.'.format(gd_name))


def get_loss_func(loss_func: str):
    if loss_func == LOSS_MAE:
        return torch.nn.L1Loss()
    elif loss_func == LOSS_MSE:
        return torch.nn.MSELoss()
    elif loss_func == LOSS_SMAE:
        return torch.nn.SmoothL1Loss()
    else:
        raise AssertionError('Unknown loss function {} was given.'.format(loss_func))
