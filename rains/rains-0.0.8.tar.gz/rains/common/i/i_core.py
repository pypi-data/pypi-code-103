# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from abc import ABCMeta
from abc import abstractmethod


class ICore(metaclass=ABCMeta):
    """
    [ 核心接口 ]
    * 无

    """

    @abstractmethod
    def start_task(self, task):
        """
        [ 开始执行 task ]
        * 接收一个 task，并执行该 task。

        [ 必要参数 ]
        * task (object): 任务对象，可以是实现 ITask 接口的任务类，或者是符合JSON译文标准的字典

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """
