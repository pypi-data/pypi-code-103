import time
import warnings
import numpy as np
import torch
from fastNLP import BatchIter, RandomSampler, Sampler, DataSetIter, DataSet
from fastNLP.core.utils import _move_model_to_device, _move_dict_value_to_device

from . import BaseTrainer
import torch.nn as nn


class Trainer(BaseTrainer):

    def __int__(self, config):
        pass

    def __init__(self, train_data, model, optimizer=None, loss=None, batch_size=8,
                 sampler=None, drop_last=False, num_workers=0, n_epochs=10, stop_step=None,
                 print_every=None, dev_data=None,
                 metrics=None, save_path=None, device=None, **kwargs):
        super(Trainer, self).__init__()
        if not isinstance(model, nn.Module):
            raise TypeError(f"The type of model must be torch.nn.Module, got {type(model)}.")

        # check save_path
        if not (save_path is None or isinstance(save_path, str)):
            raise ValueError("save_path can only be None or `str`.")

        if isinstance(train_data, BatchIter):
            if sampler is not None:
                warnings.warn("sampler is ignored when train_data is a BatchIter.")
            if num_workers > 0:
                warnings.warn("num_workers is ignored when train_data is BatchIter.")
            if drop_last:
                warnings.warn("drop_last is ignored when train_data is BatchIter.")
        if isinstance(model, nn.parallel.DistributedDataParallel):  # 如果是分布式的
            raise NotImplementedError
            pass
        else:
            # sampler check
            if sampler is not None and not isinstance(sampler, (Sampler, torch.utils.data.Sampler)):
                raise ValueError(
                    f"The type of sampler should be fastNLP.BaseSampler or pytorch's Sampler, got {type(sampler)}")
            if sampler is None:
                sampler = RandomSampler()
            elif hasattr(sampler, 'set_batch_size'):
                sampler.set_batch_size(batch_size)
        if isinstance(train_data, DataSet):
            self.data_iterator = DataSetIter(dataset=train_data, batch_size=batch_size, sampler=sampler,
                                             num_workers=num_workers, drop_last=drop_last)
        elif isinstance(train_data, BatchIter):
            self.data_iterator = train_data
            train_data = train_data.dataset
            check_code_level = -1  # 强制跳过校验
        else:
            raise TypeError("train_data type {} not support".format(type(train_data)))

        model.train()
        self.model = _move_model_to_device(model, device=device)

        self.train_data = train_data
        self.dev_data = dev_data  # If None, No validation.
        self.loss = loss
        self.optimizer = optimizer
        self.n_epochs = int(n_epochs)
        self.batch_size = int(batch_size)
        self.save_path = save_path
        self.stop_step = stop_step
        self.print_every = abs(print_every)

        self.cur_epoch = 0
        self.cur_step = 0  # 现在 步数

        if isinstance(optimizer, torch.optim.Optimizer):
            self.optimizer = optimizer
        elif optimizer is None:
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=4e-3)
        else:
            raise TypeError("optimizer can only be torch.optim.Optimizer type, not {}.".format(type(optimizer)))
        if self.optimizer is None:
            self.optimizer = torch.optim.Adam(model.parameters(), lr=1e-4, betas=(0.9, 0.999), weight_decay=0)

        self.kwargs = kwargs

    def train(self, *args, **kwargs):
        self.model.train()
        while self.cur_step <= self.stop_step:
            self.cur_epoch = self.cur_epoch + 1

            loss_list = []
            for batch_x, batch_y in self.data_iterator:  # batch_x 仅用于传入输入模型的数据
                self.cur_step = self.cur_step + 1
                _move_dict_value_to_device(batch_x, batch_y, device=self.model.device)
                prediction = self.model(batch_x)

                loss = self.loss(prediction, batch_y)

                # avg_loss += loss.item()
                loss_list.append(loss.item())
                # TODO 后期添加梯度累计
                loss.backward()

                self.optimizer.step()
                self.model.zero_grad()

                if self.cur_step % self.print_every == 0:
                    # avg_loss = float(avg_loss) / self.print_every
                    # 取 最后 print_every项做平均
                    avg_loss = float(np.array(loss_list[-self.print_every:]).mean())
                    # print_output 用于控制台或日志的打印 信息
                    print_output = "[epoch: {:>3} step: {:>4}] train loss: {:>4.6} ]".format(
                        self.cur_epoch, self.cur_step, avg_loss
                    )
                    print(print_output)
            epoch_avg_loss = float(np.array(loss_list).mean())
            print_output = "[epoch: {:>3} step: {:>4}] train epoch_loss: {:>4.6} ]".format(
                self.cur_epoch, self.cur_step, epoch_avg_loss
            )
            print(print_output)

    def valid(self, *args, **kwargs):
        self.model.eval()

    def test(self, *args, **kwargs):
        self.model.eval()
