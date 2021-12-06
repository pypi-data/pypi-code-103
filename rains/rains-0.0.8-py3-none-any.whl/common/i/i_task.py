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


class ITask(metaclass=ABCMeta):
    """
    [ 任务接口 ]
    * 任务集以函数为单位描述执行用例。

    [ 运行路径优先级 ]
    * set_class_starting(类起点)
    * set_function_starting(函数起点)
    * case_function(用例函数)
    * set_function_ending(函数终点)
    * set_class_ending(类终点)

    """

    @abstractmethod
    def set_class_starting(self):
        """
        [ 设置类起点 ]
        * 该接口将在 [ 任务类 ] 开始后执行，全程只会执行一次。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

    @abstractmethod
    def set_class_ending(self):
        """
        [ 设置类终点 ]
        * 该接口将在 [ 任务类 ] 结束后执行，全程只会执行一次。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

    @abstractmethod
    def set_function_starting(self):
        """
        [ 设置函数起点 ]
        * 该接口将在每次 [ 任务类::函数 ] 开始前执行。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

    @abstractmethod
    def set_function_ending(self):
        """
        [ 设置函数终点 ]
        * 该接口将在每次 [ 任务类::函数 ] 结束后执行。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """
