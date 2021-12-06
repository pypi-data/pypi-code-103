# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler as PyTorchScheduler
from timm.scheduler.scheduler import Scheduler as TimmScheduler

import re
from typing import List, Dict, Tuple, Any, Mapping, Optional, Union
import warnings

from .logger import Logger

Scheduler = Union[PyTorchScheduler, TimmScheduler]


class OptimizerConfig:
    """Configuration for both an optimizer and its lr-scheduler.

    Args:
        optimizer_type (str): The type name of the optimizer. e.g `torch.optim.AdamW`.
        optimizer_args (dict): The arguments of the optimizer.
        lr_scheduler_type (str): The type name of the lr_scheduler. e.g `torch.optim.lr_scheduler.MultiStepLR`.
        lr_scheduler_call (str): One of 'stepwise' or 'epochwise' or 'both.
        lr_scheduler_args (dict): The arguments of the lr_scheduler.
        network_settings (List[Dict[str, Any]]): The settings of networks to apply to.
            e.g. [{'params': 'main'}, {'params':'main.backbone', 'lr': 1e-3}]

    Usage:
        opt_config = OptimizerConfig(
            optimizer_type = 'torch.optim.AdamW',
            optimizer_args = {
                'lr': 0.001
                'betas': [0.9, 0.999]
                'weight_decay': 0.0001
            },
            lr_scheduler_type = 'torch.optim.lr_scheduler.ExponentialLR',
            lr_scheduler_args = {'gamma': 0.98},
            lr_scheduler_call = 'epochwise',
            network_settings = [
                {
                    'params': 'main.backbone.visual',
                    'lr': 0.0001
                }
            ]
        )

        optimizer, lr_scheduler = opt_config.instantiate(networks)
    """

    def __init__(self, networks: Mapping[str, nn.Module], optimizer_type: str, optimizer_args: dict,
                 lr_scheduler_type: str, lr_scheduler_args: dict,
                 network_settings: List[Dict[str, Any]],
                 lr_scheduler_call: str = 'epochwise',
                 steps_per_epoch: Optional[int] = None, logger: Optional[Logger] = None) -> None:

        # import haya
        self.optimizer_cfg = (eval(optimizer_type), optimizer_args)
        self.lr_scheduler_cfg = (eval(lr_scheduler_type), lr_scheduler_args)
        self.lr_scheduler_call = lr_scheduler_call
        assert lr_scheduler_call in {'stepwise', 'epochwise', 'both'}
        self.network_settings = network_settings
        assert isinstance(self.network_settings, list)

        self.optimizer, self.lr_scheduler = self._instantiate(
            networks, steps_per_epoch, logger)

    def scheduler_step(self, global_step):
        if self.lr_scheduler_call in {'stepwise', 'both'}:
            if isinstance(self.lr_scheduler, TimmScheduler):
                self.lr_scheduler.step_update(global_step+1)
            else:
                self.lr_scheduler.step()

    def scheduler_epoch(self, epoch):
        if self.lr_scheduler_call in {'epochwise', 'both'}:
            if isinstance(self.lr_scheduler, TimmScheduler):
                self.lr_scheduler.step(epoch)
            else:
                self.lr_scheduler.step()

    def load_state_dict(self, state):
        opt_state, sch_state = state
        self.optimizer.load_state_dict(opt_state)
        self.lr_scheduler.load_state_dict(sch_state)

    def state_dict(self):
        return (self.optimizer.state_dict(), self.lr_scheduler.state_dict())

    def _instantiate(self, networks: Mapping[str, nn.Module],
                     steps_per_epoch: Optional[int] = None,
                     logger: Optional[Logger] = None) -> Tuple[Optimizer, Scheduler]:
        """Instantiate the optimizer and the lr_scheduler for the networks.

        Args:
            networks (Mapping[str, nn.Module]): The networks to attach to. 
                e.g. {'main': SomeNetwork}
        """

        optimizer_type, optimizer_args = self.optimizer_cfg

        def _named_parameters(pattern: str) -> Tuple[List[torch.Tensor], List[str]]:
            collected_names = []
            collected_params = []
            for network_name, model in networks.items():
                if hasattr(model, '_ema_cfg'):
                    continue
                for param_name, param in model.named_parameters():
                    name = f'{network_name}.{param_name}'
                    if re.match(pattern, name):
                        collected_names.append(name)
                        collected_params.append(param)
            return collected_params, collected_names

        # interpret parameter settings
        param_groups = []

        all_collected_names = set()
        for network_setting in self.network_settings:
            assert isinstance(network_setting, dict)
            param_group = dict()
            for key, val in network_setting.items():
                if key == 'params':
                    assert isinstance(val, str)
                    val, names = _named_parameters(val)
                    if len(set(names) & all_collected_names) > 0:
                        raise RuntimeError(
                            f'Duplicated parameter settings for '
                            f'parameter names: {names & all_collected_names}')
                    all_collected_names |= set(names)

                param_group[key] = val
            param_groups.append(param_group)
        # check whether we lost some params
        all_existing_names = set(_named_parameters('.*')[1])
        if len(all_existing_names-all_collected_names) > 0:
            msg = (f'Some parameters are not included in parameter settings: '
                   f'{all_existing_names-all_collected_names}')
            if logger is None:
                warnings.warn(msg)
            else:
                logger.log_info(msg)

        optimizer: Optimizer = optimizer_type(
            param_groups, **optimizer_args)
        lr_scheduler_type, lr_scheduler_args = self.lr_scheduler_cfg

        # parse lr_scheduler_args
        _lr_scheduler_args = dict()
        for name, val in lr_scheduler_args.items():
            if isinstance(val, str) and '{steps_per_epoch}' in val:
                _lr_scheduler_args[name] = eval(
                    val.format(steps_per_epoch=steps_per_epoch))
                print(
                    f'NOTE: lr_scheduler_args[{name}]: {val} '
                    f'-> {_lr_scheduler_args[name]}')
            else:
                _lr_scheduler_args[name] = val

        lr_scheduler: Scheduler = lr_scheduler_type(
            optimizer, **_lr_scheduler_args)
        return optimizer, lr_scheduler
