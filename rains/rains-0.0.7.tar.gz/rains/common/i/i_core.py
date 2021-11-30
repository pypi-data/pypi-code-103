# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from abc import ABCMeta
from abc import abstractmethod


class ICore(metaclass=ABCMeta):
    """
    核心接口
    """

    @abstractmethod
    def start_task(self, task):
        """
        开始执行 task

        * 接收一个 task，并执行该 task。

        Args:
            task (object): 任务对象，可以是实现 ITask 接口的任务类，或者是符合JSON译文标准的字典

        """
