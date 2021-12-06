# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.kit.web.web_plant import WebPlant


class WebModel(object):
    """
    WEB模型
    """

    plant: WebPlant

    def __init__(self, web_plant: WebPlant):
        """
        初始化

        * 构建页面模型主要由 Plant 构建类完成，实例化页面模型时需传递 Plant 实例。

        """
        self.plant = web_plant
