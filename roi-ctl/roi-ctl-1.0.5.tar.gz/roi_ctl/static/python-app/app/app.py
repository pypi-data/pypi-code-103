#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
   @File    :   __init__.py
   @Create  :   2021/09/06 19:45:16
   @Author  :   Your Name
   @Update  :   2021/09/06
   @License :   (C)Copyright 2014-2021 SmartAHC All Rights Reserved 
   @Desc    :   Coding Below
"""

from .app_product import product
from .app_logger import logger

class App():

    """
    项目主入口
    """

    def __init__(self):
        """
        根据需要初始化
        """
        logger.debug("APP RUNNING")

    def run(self):
        """
        主函数入口
        """
        pass
