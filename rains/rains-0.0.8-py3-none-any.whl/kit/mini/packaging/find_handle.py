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
from minium import WXMinium

from Rains2.common.log import Log
from Rains2.kit.mini.mini_element_structure import MiniElementStructure


class MiniFindHandle(object):
    """
    [ 小程序元素定位器 ]

    * 基于 minium 原生定位函数的封装。

    """

    _log = Log()
    """ [ 日志服务 ] """

    _driver: WXMinium
    """ [ 原生驱动对象 ] """

    def __init__(self, base_driver: WXMinium):
        """
        [ 初始化 ]

        Args:
            base_driver (WXMinium): 小程序驱动对象

        """
        self._driver = base_driver

    # func boundary -----------------------------------------------------------------------------------------------

    def find(self,
             mini_element_structure: MiniElementStructure,
             wait: int = 20) -> list:
        """
        [ 元素定位 ]

        * 根据参数描述从当前页面上定位元素列表。

        Args:
            mini_element_structure (str): 小程序元素结构体
            wait (int): 查找元素所等待的显式等待时长

        Return:
            已获取定位的元素列表

        """

        try:

            time.sleep(0.2)

            # 获取当前页面对象
            page: Page = self._driver.app.get_current_page()

            return page.get_elements(
                selector=mini_element_structure.selector,
                max_timeout=wait,
                inner_text=mini_element_structure.inner_text,
                text_contains=mini_element_structure.text_contains,
                value=mini_element_structure.value,
                index=-1
            )

        except BaseException as e:
            raise Exception(f'定位元素时发生了异常:: { e }')
