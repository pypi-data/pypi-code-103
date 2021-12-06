# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.kit.mini.mini_plant import MiniPlant


class MiniModel(object):
    """
    [ 小程序模型 ]
    * 无

    """

    plant: MiniPlant

    def __init__(self, mini_plant: MiniPlant):
        """
        [ 初始化 ]
        * 构建页面模型主要由 Plant 构建类完成，实例化页面模型时需传递 Plant 实例。

        [ 必要参数 ]
        * mini_plant (MiniPlant) : 小程序工厂构建类

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self.plant = mini_plant
