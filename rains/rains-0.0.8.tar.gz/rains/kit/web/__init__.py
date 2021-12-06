# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.kit.web.web_task import WebTask
from rains.kit.web.web_core import WebCore
from rains.kit.web.web_core import BROWSER_TYPE
from rains.kit.web.web_plant import BY
from rains.kit.web.web_plant import WebPlant
from rains.kit.web.web_plant import WebPlantElement
from rains.kit.web.web_model import WebModel

WebElement = WebPlantElement

__all__ = ['WebTask', 'WebCore', 'BROWSER_TYPE', 'BY', 'WebPlant', 'WebElement', 'WebModel']
