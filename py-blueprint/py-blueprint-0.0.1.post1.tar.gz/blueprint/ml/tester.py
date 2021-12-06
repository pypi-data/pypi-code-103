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

from typing import Mapping, List, Dict, Optional, Any

import os
import torch
from torch import nn
import torch.distributed as dist
import pickle as pk

from .dataprocessor import DataProcessor
from .logger import Logger
from .task import Task
from .scorer import Scorer
from .trainer import Trainer, _interpret_ema_networks
from .util import _load_states


__all__ = ['Tester', 'tester_of_trainer']


def tester_of_trainer(trainer: Trainer, outputs_dir: str,
                      eval_dataprocessors: Optional[Mapping[str, DataProcessor]],
                      test_dataprocessors: Optional[Mapping[str, DataProcessor]],
                      logger: Optional[Logger] = None, epoch: Optional[int] = None):
    if eval_dataprocessors is None:
        eval_dataprocessors = trainer.eval_dataprocessors
    if test_dataprocessors is None:
        test_dataprocessors = dict()
    if logger is None:
        logger = trainer.logger
    return Tester(outputs_dir, trainer.states_dir,
                  eval_dataprocessors, test_dataprocessors,
                  trainer.networks, trainer.task_module, trainer.scorer,
                  logger, init_epoch=epoch)


class Tester:
    """A tester.
    """

    def __init__(self,
                 outputs_dir: str,
                 trainer_states_dir: str,
                 eval_dataprocessors: Mapping[str, DataProcessor],
                 test_dataprocessors: Mapping[str, DataProcessor],
                 networks: Mapping[str, nn.Module],
                 task_module: Task,
                 scorer: Scorer,
                 logger: Logger,
                 init_epoch: Optional[int] = None,
                 init_global_step: Optional[int] = None,
                 save_eval_results: bool = True):

        self.trainer_states_dir = trainer_states_dir
        self.outputs_dir = outputs_dir
        self.eval_dataprocessors = eval_dataprocessors
        self.test_dataprocessors = test_dataprocessors

        self.networks = _interpret_ema_networks(networks)
        self.task_module = task_module
        self.scorer = scorer

        self.logger = logger
        self.logger.setup(outputs_dir)
        self.logger.log_info(f'trainer_states_dir={trainer_states_dir}')

        self.init_global_step = init_global_step
        self.init_epoch = init_epoch

        self.global_step = None
        self.epoch = None

        self.save_eval_results = save_eval_results

    def __call__(self):
        if not dist.is_initialized():
            raise RuntimeError(
                "Requires torch.distributed package to be initialized")

        self.epoch = 0
        self.global_step = 0

        self._load_test_states()

        self.task_module.setup_networks(self.networks)
        task_module = nn.parallel.DistributedDataParallel(
            self.task_module.float().cuda(), device_ids=[torch.cuda.current_device()],
            find_unused_parameters=True)
        task_module.eval()

        for eval_name, eval_dataprocessor in self.eval_dataprocessors.items():
            self.logger.log_info(
                f'evaluating {eval_dataprocessor.num_steps_of_epoch(0)} '
                f'batches from {eval_name} ...')
            self.scorer.init_evaluation()
            for idx, result_data in enumerate(eval_dataprocessor.iterate_final_result(self.task_module)):
                self.scorer.evaluate(result_data)

                if self.save_eval_results:
                    save_dir = os.path.join(
                        self.outputs_dir, eval_name)
                    os.makedirs(save_dir, exist_ok=True)
                    with open(os.path.join(save_dir, f'{idx}_rank{dist.get_rank()}.pk'), 'wb') as f:
                        pk.dump(result_data, f)

            scores = self.scorer.finalize_evaluation()
            self.logger.log_numbers(scores,
                                    global_step=self.global_step,
                                    epoch=self.epoch, tag=f'eval.{eval_name}')

    def _load_test_states(self):
        states = _load_states(self.trainer_states_dir, self.logger,
                              global_step=self.init_global_step, epoch=self.init_epoch)
        if states is not None:
            self.epoch = states['epoch']
            self.global_step = states['global_step']
            self.logger.log_info(
                f'epoch={self.epoch}, global_step={self.global_step}')
            for net_name, net in self.networks.items():
                net.load_state_dict(states['networks'][net_name])
            del states
        else:
            raise RuntimeError(
                f'Failed to load any states from {self.trainer_states_dir}.')
