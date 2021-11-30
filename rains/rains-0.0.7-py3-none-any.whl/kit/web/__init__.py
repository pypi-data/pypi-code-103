# !/usr/bin/env python
# coding:utf-8

# Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.

# Based on the Apache License 2.0 open source protocol.

__author__ = 'quinn.7@foxmail.com'


from rains.kit.web.task import WebTask
from rains.kit.web.core import WebCore
from rains.kit.web.core import BROWSER_TYPE
from rains.kit.web.plant import BY
from rains.kit.web.plant import WebPlant
from rains.kit.web.plant import WebPlantElement
from rains.kit.web.model import WebModel

WebElement = WebPlantElement

__all__ = ['WebTask', 'WebCore', 'BROWSER_TYPE', 'BY', 'WebPlant', 'WebElement', 'WebModel']
