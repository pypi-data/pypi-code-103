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

import os
from typing import Mapping, List, Dict, Optional, Any, Union, Set
from contextlib import contextmanager

import torch
from torch import nn
import torch.distributed as dist

from ..context import Context

from .ema_config import EMAConfig, _interpret_ema_networks

from .dataprocessor import DataProcessor
from .logger import Logger
from .task import ForwardFlags, Task
from .scorer import Scorer
from .optimizer import OptimizerConfig
from .stats import StatSummary
from .util import _load_states, _save_states, barrier, accumulate


class Trainer:
    """A standard trainer for supervised training. You should use DistributedGPURun with it.
    """

    def __init__(self,
                 states_dir: str,
                 outputs_dir: str,
                 train_dataprocessor: DataProcessor,
                 eval_dataprocessors: Mapping[str, DataProcessor],
                 networks: Mapping[str, Union[nn.Module, EMAConfig]],
                 task_module: Task,
                 scorer: Scorer,
                 optimizer_cfg: dict,
                 logger: Logger,
                 cont_opti: bool = True,
                 num_states_kept: Optional[int] = None,
                 max_epoches: Optional[int] = None,
                 enable_amp: bool = False,
                 states_save_interval: int = 1,
                 eval_interval: int = 1,
                 states_save_extra_steps: List[int] = [],
                 _ctx: Optional[Context] = None):

        self.context = _ctx

        self.outputs_dir = outputs_dir
        self.states_dir = states_dir

        self.train_dataprocessor = train_dataprocessor
        self.eval_dataprocessors = eval_dataprocessors

        self.networks = _interpret_ema_networks(networks)

        self.task_module = task_module
        self.scorer = scorer

        self.logger = logger
        self.logger.setup(self.outputs_dir)
        self.logger.log_info(f'outputs_dir: {self.outputs_dir}')
        self.logger.log_info(f'states_dir: {self.states_dir}')

        self.optimizer_cfg = OptimizerConfig(
            networks=self.networks,
            steps_per_epoch=self.train_dataprocessor.num_steps_of_epoch(0),
            logger=logger, **optimizer_cfg)

        self.rank = self.world_size = None

        self.cont_opti = cont_opti
        self.num_states_kept = num_states_kept

        self.max_epoches = max_epoches
        self.states_save_interval = states_save_interval
        self.eval_interval = eval_interval
        self.states_save_extra_steps = states_save_extra_steps

        self.enable_amp = enable_amp
        self.amp_scaler = None
        if self.enable_amp:
            self.amp_scaler = torch.cuda.amp.GradScaler()

        self.global_step = None
        self.epoch = None

        self.world_size = self.rank = None
        self.debug_loss = _ctx.debug_loss
        self.detect_anomaly = _ctx.detect_anomaly

    @contextmanager
    def _train_scope(self):
        with torch.cuda.amp.autocast(enabled=self.enable_amp):
            with torch.autograd.set_detect_anomaly(self.detect_anomaly):
                yield

    def _backward(self, loss: torch.Tensor):
        if self.amp_scaler is None:
            loss.backward()
        else:
            self.amp_scaler.scale(loss).backward()

    def _optimizer_step(self):
        if self.amp_scaler is None:
            self.optimizer_cfg.optimizer.step()
        else:
            self.amp_scaler.step(self.optimizer_cfg.optimizer)
            self.amp_scaler.update()

        # update ema modules
        for _, net in self.networks.items():
            if hasattr(net, '_ema_cfg'):
                ema_cfg: EMAConfig = net._ema_cfg
                orig_net = self.networks[ema_cfg.network_name]
                decay = ema_cfg.decay
                accumulate(net, orig_net, decay=decay)

    def __call__(self):
        if not dist.is_initialized():
            raise RuntimeError(
                "Requires torch.distributed package to be initialized")
        self.rank = dist.get_rank()
        assert self.rank is not None
        self.world_size = dist.get_world_size()
        assert self.world_size is not None

        if self.rank == 0:
            os.makedirs(self.outputs_dir, exist_ok=True)
            os.makedirs(self.states_dir, exist_ok=True)

        self.epoch = 0
        self.global_step = 0

        self._load_train_states()

        self.task_module.setup_networks(self.networks)
        task_module = nn.parallel.DistributedDataParallel(
            self.task_module.float().cuda(), device_ids=[torch.cuda.current_device()],
            find_unused_parameters=True)

        while self.max_epoches is None or self.epoch < self.max_epoches:
            barrier()

            task_module.train()
            loss_summary_this_epoch = StatSummary()

            self.optimizer_cfg.optimizer.zero_grad()
            num_steps = self.train_dataprocessor.num_steps_of_epoch(self.epoch)
            self.logger.log_info(
                f'There will be {num_steps} training steps in this epoch.')

            for step, data in enumerate(self.train_dataprocessor.iterate_input(self.epoch)):
                time_to_save_outputs = step == num_steps - 1 or self.global_step == 0
                if step >= num_steps:
                    break

                if self.global_step in self.states_save_extra_steps:
                    self._save_train_states(losses=None)

                # forward
                with self._train_scope():
                    loss, named_losses, _, images = task_module(
                        data, ForwardFlags(with_losses=True,
                                           with_outputs=False,
                                           with_images=time_to_save_outputs))

                    if self.debug_loss:
                        print(f'loss={loss.item()}')

                # backward
                self.optimizer_cfg.optimizer.zero_grad()
                # self.amp_scaler.
                self._backward(loss)

                # update
                self._optimizer_step()
                self.optimizer_cfg.scheduler_step(self.global_step)

                # accumulate loss values
                loss_summary_this_epoch.update(named_losses)

                # save output images at the end of each training epoch
                if time_to_save_outputs:
                    self.logger.log_numbers(
                        loss_summary_this_epoch.get_averages(),
                        global_step=self.global_step, epoch=self.epoch, tag='train')
                    self.logger.log_batched_images(
                        images, global_step=self.global_step, epoch=self.epoch, tag='train')

                self.global_step += 1

            self.optimizer_cfg.scheduler_epoch(self.epoch)

            self.epoch += 1

            barrier()

            if self.epoch % self.states_save_interval == 0:
                self._save_train_states(losses=None)

            if self.epoch % self.eval_interval == 0:
                task_module.eval()
                # evaluate on the eval_dataprocessor using the scorer
                for eval_name, eval_dataprocessor in self.eval_dataprocessors.items():
                    self.logger.log_info(
                        f'evaluating {eval_dataprocessor.num_steps_of_epoch(0)} '
                        f'batches from {eval_name} ...')
                    self.scorer.init_evaluation()
                    for result_data in eval_dataprocessor.iterate_final_result(self.task_module):
                        self.scorer.evaluate(result_data)
                    scores = self.scorer.finalize_evaluation()
                    self.logger.log_numbers(scores,
                                            global_step=self.global_step,
                                            epoch=self.epoch, tag=f'eval.{eval_name}')

                # show GPU status
                if self.epoch == self.eval_interval and torch.cuda.current_device() == 0:
                    os.system('nvidia-smi')

    def _load_train_states(self):
        states = _load_states(self.states_dir, self.logger)
        if states is not None:
            self.epoch = states['epoch']
            self.global_step = states['global_step']
            for net_name, net in self.networks.items():
                net.load_state_dict(states['networks'][net_name])
            if self.cont_opti:
                self.optimizer_cfg.load_state_dict(states['optimizer'])
            del states

    def _save_train_states(self, losses=None):
        if self.rank == 0:
            if losses is None:
                losses = dict()
            states = {'epoch': self.epoch, 'global_step': self.global_step,
                      'losses': losses}
            states['networks'] = {name: net.state_dict()
                                  for name, net in self.networks.items()}
            states['optimizer'] = self.optimizer_cfg.state_dict()

            _save_states(states, self.states_dir,
                         losses=losses,
                         global_step=self.global_step, epoch=self.epoch,
                         num_states_kept=self.num_states_kept,
                         always_kept_steps=[],
                         always_kept_epoches=[],
                         logger=self.logger)
            self.logger.log_info(
                'all states saved with global_step=%d' % self.global_step)
