# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.webdriver import RemoteWebDriver

from rains.common.log import Log
from rains.kit.web.packaging.web_element_structure import WebElementStructure


class WebFindHandle(object):
    """
    WEB元素定位器
    """

    _log = Log()
    """ 日志服务 """

    _driver: RemoteWebDriver
    """ 原生驱动对象 """

    _web_driver_wait: WebDriverWait = WebDriverWait
    """ 原生驱动显示等待封装 """

    def __init__(self, base_driver: RemoteWebDriver):
        """
        初始化

        Args:
            base_driver (RemoteWebDriver): 原生驱动对象

        """
        self._driver = base_driver

    def find(self, element_structure: WebElementStructure,
             wait: int = 15, tolerance: bool = False) -> list:
        """
        元素定位

        * 接受一个 WebElementStructure 对象，并根据其描述从当前页面上定位元素列表。

        Args:
            element_structure (ElementStructure): 元素结构体
            wait (int): 查找元素所等待的显式等待时长
            tolerance (bool): 容错模式，为 True 则表示定位不到元素也不报错，返回空列表

        Return:
            已获取定位的元素列表

        """
        # 解析元素搜索范围
        search_range = self._analysis_search_range(element_structure, wait)

        # 开始定位UI元素
        elements = self._base_explicitly_wait_find_element(
            by_key=element_structure.by_key,
            by_value=element_structure.by_value,
            driver=search_range,
            wait=wait,
            tolerance=tolerance)

        return elements

    def _analysis_search_range(self, element_structure: WebElementStructure, wait: int):
        """
        解析元素搜索范围

        * 如果元素结构体中携带了锚元素则会返回定位的锚元素对象, 否则返回驱动。

        Args:
            element_structure (ElementStructure): WEB元素结构体
            wait (int): 查找元素所等待的显式等待时长

        Return:
            锚元素对象 or 驱动对象

        """
        search_range = self._driver

        if element_structure.anchor_by_key:
            search_range = self._base_explicitly_wait_find_element(
                by_key=element_structure.anchor_by_key,
                by_value=element_structure.anchor_by_value,
                driver=search_range,
                wait=wait,
                tolerance=False)[element_structure.anchor_location_id]

        return search_range

    def _base_explicitly_wait_find_element(self,
                                           by_key: str,
                                           by_value: str,
                                           driver,
                                           wait: int,
                                           tolerance: bool) -> list:
        """
        原生 WebDriverWait 封装

        * 封装 WebDriverWait 全局显示等待获取函数。
        * 该函数将在每 0.5 秒时遍历一次页面，直到找到元素或者等待(wait)超时。
        * 如果容错开关(tolerance)为 True, 则表示定位不到元素时返回空列表。

        Return:
            已获取定位的元素列表 or 空列表

        """
        try:
            return self._web_driver_wait(driver, wait, poll_frequency=0.5, ignored_exceptions=None)\
                .until(ec.presence_of_all_elements_located((by_key, by_value)))

        except TimeoutException:
            # 触发异常时，如果容错开关(tolerance)为 True，则不抛出异常，仅返回空列表
            if tolerance:
                return []
            else:
                raise Exception(f'定位器获取不到元素！')
