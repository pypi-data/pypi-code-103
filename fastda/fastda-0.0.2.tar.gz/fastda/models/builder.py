# Author: Vincent Zhang
# Mail: zhyx12@gmail.com
# ----------------------------------------------
import torch.nn as nn
from mmcv.utils import Registry, build_from_cfg

CLS_MODELS = Registry('models')


def build_models(cfg, default_args=None):
    if isinstance(cfg, list):
        modules = [
            build_from_cfg(cfg_, CLS_MODELS, default_args) for cfg_ in cfg
        ]
        return nn.Sequential(*modules)
    else:
        return build_from_cfg(cfg, CLS_MODELS, default_args)

