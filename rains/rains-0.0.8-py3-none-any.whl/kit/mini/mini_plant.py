# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from rains.common.log import Log

from rains.kit.mini.mini_engine import MiniEngine
from rains.kit.mini.packaging.mini_element_structure import MiniElementStructure

from rains.kit.mini.packaging.mini_plant_view import MiniPlantView
from rains.kit.mini.packaging.mini_plant_element import MiniPlantElement


class MiniPlant(object):
    """
    [ 小程序工厂构建类 ]
    * 工厂构建类提供了对小程序视图与控件元素的封装。

    """

    _log = Log()
    """ [ 日志服务 ] """

    _mini_engine: MiniEngine
    """ [ 引擎对象 ] """

    def __init__(self, mini_engine: MiniEngine):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * mini_engine (MiniEngine) : 小程序引擎对象

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._mini_engine = mini_engine

        # 如果引擎中的驱动未启动，则启动
        if not self._mini_engine.driver:
            self._mini_engine.run()

    @property
    def engine(self):
        return self._mini_engine

    @property
    def driver(self):
        return self._mini_engine.driver

    @property
    def view(self) -> MiniPlantView:
        """
        [ 小程序视图 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (MiniPlantView) : 小程序视图对象

        """

        return MiniPlantView(self._mini_engine)

    def element(self,
                page: str,
                name: str,
                selector: str) -> MiniPlantElement:
        """
        [ 小程序元素控件 ]
        * 基于元素特征构建指向该元素的元素控件对象。
        * 元素控件对象封装了针对元素的一些操作元素，例如鼠标点击、键盘输入等等。

        [ 必要参数 ]
        * page (str) : 页面名称
        * name (str) : 组件名称
        * selector (str) : css选择器或以/或//开头的xpath

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (MiniPlantElement) : 小程序元素对象

        """

        element_structure = MiniElementStructure(
            page=page,
            name=name,
            selector=selector
        )

        return MiniPlantElement(self._mini_engine, element_structure)
