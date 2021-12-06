# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import time

from minium import Page
from minium import Minium

from rains.common.log import Log
from rains.kit.mini.packaging.mini_element_structure import MiniElementStructure


class MiniFindHandle(object):
    """
    [ 小程序元素定位器 ]
    * 基于 minium 原生定位函数的封装。

    """

    _log = Log()
    """ [ 日志服务 ] """

    _driver: Minium
    """ [ 原生驱动对象 ] """

    def __init__(self, base_driver: Minium):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * base_driver (WXMinium) : 小程序驱动对象

        """

        self._driver = base_driver

    def find(self,
             mini_element_structure: MiniElementStructure,
             wait: int = 15) -> list:
        """
        [ 元素定位 ]
        * 根据参数描述从当前页面上定位元素列表。

        [ 必要参数 ]
        * mini_element_structure (str) : 小程序元素结构体

        [ 可选参数 ]
        * wait (int) : 查找元素所等待的显式等待时长

        [ 返回内容 ]
        * 已获取定位的元素列表

        """

        try:

            time.sleep(0.2)
            page: Page = self._driver.app.get_current_page()

            return page.get_elements(
                selector=mini_element_structure.selector,
                max_timeout=wait,
            )

        except BaseException as e:
            raise Exception(f'定位元素时发生了异常:: { e } !')
