# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from selenium.webdriver.common.by import By

from rains.common.log import Log

from rains.kit.web.web_engine import WebEngine
from rains.kit.web.packaging.web_plant_view import WebPlantView
from rains.kit.web.packaging.web_plant_element import WebPlantElement
from rains.kit.web.packaging.web_element_structure import WebElementStructure


BY = By


class WebPlant(object):
    """
    [ Web工厂构建类 ]
    * 工厂构建类提供了对浏览器视图与控件元素的封装。
    * 浏览器视图: 封装了浏览器本身的功能，例如访问URL、管理标签页、控制弹窗、上传文件等。
    * 控件元素：封装了对页面元素的操作功能，如控制鼠标、控制输入框、下拉框、判断元素是否存在等。

    """

    _log = Log()
    """ 日志服务 """

    _web_engine: WebEngine
    """ 引擎对象 """

    def __init__(self, web_engine: WebEngine):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * web_engine (WebEngine): WEB引擎对象

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._web_engine = web_engine

        # 如果引擎中的驱动未启动，则启动
        if not self._web_engine.driver:
            self._web_engine.run()

    @property
    def engine(self):
        return self._web_engine

    @property
    def driver(self):
        return self._web_engine.driver

    @property
    def view(self) -> WebPlantView:
        """
        [ Web视图 ]
        * 提供针对浏览器本身的操作函数，例如访问URL，最大化窗口，截图PNG等等。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (WebPlantView) : Web视图对象

        """

        return WebPlantView(self._web_engine)

    def element(self,
                page: str,
                name: str,
                by_key: str,
                by_value: str,
                anchor_by_key: str = None,
                anchor_by_value: str = None,
                anchor_location_id: int = None) -> WebPlantElement:
        """
        [ Web元素控件 ]
        * 基于元素特征构建指向该元素的元素控件对象。
        * 元素控件对象封装了针对元素的一些操作元素，例如鼠标点击、键盘输入等等。

        [ 必要参数 ]
        * page (str) : 页面名称
        * name (str) : 组件名称
        * by_key (str) : 元素定位策略
        * by_value (str) : 元素定位策略对应的值

        [ 可选参数 ]
        * anchor_by_key (str) : 锚点元素定位策略
        * anchor_by_value (str) : 锚点元素定位策略
        * anchor_location_id (str) : 锚点元素定位ID

        [ 返回内容 ]
        * (WebPlantElement) : Web元素控件对象

        """

        element_structure = WebElementStructure(page, name, by_key, by_value,
                                                anchor_by_key, anchor_by_value, anchor_location_id)

        return WebPlantElement(self._web_engine, element_structure)
