# Adapted from score written by wkentaro
# https://github.com/wkentaro/pytorch-fcn/blob/master/torchfcn/utils.py

import numpy as np
from torchvision.utils import make_grid
import torch
import random
from .logger import get_root_logger
from .writer import get_root_writer


class averageMeter(object):
    """Computes and stores the average and current value"""

    def __init__(self, name=None):
        self.reset()
        self.name = name

    def reset(self):
        self.val = 0.0
        self.sum = 0.0
        self.count = 0.0

    def update(self, val, n=1):
        self.val = val
        self.sum += val
        self.count += n

    @property
    def avg(self):
        return self.sum / self.count

    def log_to_writer(self, writer, iteration, name_prefix):
        writer.add_scalar('{}/{}'.format(name_prefix, self.name), self.avg, iteration)
        return self.name + ':{:.4f}\t'.format(self.avg)


class lrRecoder(object):
    def __init__(self, scheduler_dict, name=None):
        self.scheduler_dict = scheduler_dict

    def update(self, val):
        pass

    def log_to_writer(self, writer, iteration, name_prefix):
        log_str = ''
        for name in self.scheduler_dict:
            temp_lr = self.scheduler_dict[name].get_lr()[0]
            writer.add_scalar('{}/{}'.format(name_prefix, name), temp_lr, iteration)
            log_str += '{}_lr: {:.2e}\t'.format(name, temp_lr)
        return log_str

    def reset(self):
        self.log_str = ''


def _get_metric_instance(name):
    try:
        return {
            'avgmeter': averageMeter,
            'lrrecoder': lrRecoder,
        }[name]
    except:
        raise RuntimeError("metric type {} not available".format(name))


class runningMetric(object):
    def __init__(self, ):
        self.metrics = {}
        self.log_intervals = {}
        self.log_str_flag = {}
        self.logger = get_root_logger()
        self.writer = get_root_writer()

    def add_metrics(self, metric_name, group_name, metric_type, log_interval=None, init_param_list=(),
                    init_param_dict=None, log_str_flag=True):
        if group_name not in self.metrics:
            assert log_interval is not None, 'you should specify log interval when first add metric'
            self.metrics[group_name] = {}
            self.log_intervals[group_name] = log_interval
            self.log_str_flag[group_name] = log_str_flag
        else:
            assert log_interval is None or log_interval == self.log_intervals[
                group_name], 'log interval {} is not consistent with {}'.format(log_interval,
                                                                                self.log_intervals[group_name])
            assert log_str_flag is None or log_str_flag == self.log_str_flag[group_name], 'log str flag not match'
        if isinstance(metric_name, (tuple, list, str)):
            metric_name = (metric_name,) if isinstance(metric_name, str) else metric_name
            for name in metric_name:
                temp_param_dict = {'name': name}
                if init_param_dict is not None:
                    temp_param_dict.update(init_param_dict)
                self.metrics[group_name][name] = _get_metric_instance(metric_type)(*init_param_list,
                                                                                   **temp_param_dict)
        else:
            raise RuntimeError('log name should be str or tuple list of str')

    def update_metrics(self, batch_metric):
        for group_name in batch_metric:
            if group_name in self.metrics.keys():  # 增加了group name是否在本running_metrics的判断
                temp_group = batch_metric[group_name]
                for name in temp_group:
                    self.metrics[group_name][name].update(temp_group[name])

    def log_metrics(self, iteration, force_log=False):
        for group_name in self.metrics:
            # print('group name {}, log interval {}'.format(group_name,self.log_intervals[group_name]))
            if (iteration % self.log_intervals[group_name] == 0 and iteration > 0) or force_log:
                log_str = 'iter:{}---'.format(iteration)
                for name in self.metrics[group_name]:
                    temp_log_str = self.metrics[group_name][name].log_to_writer(self.writer, iteration, group_name)
                    if self.log_str_flag[group_name]:
                        log_str += temp_log_str
                    # 重置
                    self.metrics[group_name][name].reset()
                if self.log_str_flag[group_name]:
                    self.logger.info(log_str)

    def reset_metrics(self, ):
        for group_name in self.metrics.keys():
            temp_group = self.metrics[group_name]
            for name in temp_group:
                self.metrics[group_name][name].reset()
