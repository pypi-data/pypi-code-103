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


class IEngine(metaclass=ABCMeta):
    """
    [ 引擎接口 ]
    * 无

    """

    @abstractmethod
    def get_state(self) -> bool:
        """
        [ 获取引擎状态 ]
        * 获取当前引擎状态，启动中返回 True，否则返回 False。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (Bool) : 当前引擎状态

        """

    @abstractmethod
    def run(self):
        """
        [ 运行引擎 ]
        * 驱动与定位器的实例化。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

    @abstractmethod
    def end(self):
        """
        [ 结束引擎 ]
        * 退出并销毁当前持有的驱动与定位器。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

    @abstractmethod
    def reset(self):
        """
        [ 重置引擎 ]
        * 将引擎重置至初始阶段。
        * 与 end() 相比，该函数只是重置引擎至初始状态，而不是注销。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """
