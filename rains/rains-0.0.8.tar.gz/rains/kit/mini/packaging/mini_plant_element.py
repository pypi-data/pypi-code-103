# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['MiniPlantElement']


from rains.common.log import Log

from rains.kit.mini.mini_engine import MiniEngine
from rains.kit.mini.packaging.mini_element_structure import MiniElementStructure


class MiniPlantElement(object):
    """
    [ 小程序元素控件 ]
    * 基于元素特征构建指向该元素的元素控件对象。

    """

    _log = Log()
    """ [ 日志服务 ] """

    _mini_engine: MiniEngine
    """ [ 引擎对象 ] """

    _element_structure: MiniElementStructure
    """ [ 元素结构体 ] """

    _element_container: list = []
    """ [ 元素列表容器 ] """

    def __init__(self,
                 mini_engine: MiniEngine,
                 mini_element_structure: MiniElementStructure):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * mini_engine (MiniEngine): 小程序引擎对象
        * mini_element_structure (MiniElementStructure): 小程序元素结构体

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._mini_engine = mini_engine
        self._element_structure = mini_element_structure

    def _log_output(self, message: str, log: bool):
        """
        [ 日志输出 ]
        * 无

        [ 必要参数 ]
        * message (str) : 输出信息
        * log (bool) : 输出判断值

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if log:
            self._log.info(f'执行核心[{ self._mini_engine.id }]::'
                           f'{ self._element_structure.page }::'
                           f'{ self._element_structure.name }::'
                           f'{ message }')

    def _err_output(self, message: str):
        """
        [ 错误输出 ]
        * 无

        [ 必要参数 ]
        * message (str) : 输出信息

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        raise Exception((f'执行核心[{ self._mini_engine.id }]::'
                         f'{ self._element_structure.page }::'
                         f'{ self._element_structure.name }::'
                         f'{ message }'))

    def _analytical_elements(self, wait: int = 15) -> list:
        """
        [ 解析函数 ]
        * 每一次调用页面元素组件的方法时，都会调用该函数，以更新定位结果，确认组件是否存在于当前页面中。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * wait (int) : 查找元素所等待的显式等待时长

        [ 返回内容 ]
        * 元素列表容器

        """

        try:
            self._element_container = \
                self._mini_engine.find_handle.find(self._element_structure, wait)

            return self._element_container

        except BaseException as e:
            self._err_output(f'元素控件精灵类解析异常:: { e } !')

    @property
    def get(self):
        """
        [ 小程序元素控件'获取'相关函数 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        return _MiniPlantElementMapGet(self._mini_engine,
                                       self._analytical_elements,
                                       self._log_output,
                                       self._err_output)

    @property
    def mouse(self):
        """
        [ 小程序元素控件'鼠标'相关函数 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        return _MiniPlantElementMapMouse(self._mini_engine,
                                         self._analytical_elements,
                                         self._log_output,
                                         self._err_output)

    @property
    def input(self):
        """
        [ 小程序元素控件'输入框'相关函数 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        return _MiniPlantElementMapInput(self._mini_engine,
                                         self._analytical_elements,
                                         self._log_output,
                                         self._err_output)

    def switch(self, eid: int = 0, log: bool = True):
        """
        [ 改变 switch 组件的状态 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].switch()
            self._log_output(f'改变 switch 组件的状态', log)

            return self

        except BaseException as err:
            self._err_output(f'改变 switch 组件的状态异常::{ err }')

    def slide_to(self, value: int, eid: int = 0, log: bool = True):
        """
        [ slider 组件滑动到指定数值 ]
        * 无

        [ 必要参数 ]
        * value (int) : 数值

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].slide_to(value)
            self._log_output(f'slider 组件滑动到指定数值[{ value }]', log)

            return self

        except BaseException as e:
            self._err_output(f'slider 组件滑动到指定数值异常:: { e }')

    def pick(self, value: int or str, eid: int = 0, log: bool = True):
        """
        [ picker 选择器组件选值 ]
        * value 的取值:
        * selector / multiSelector / region 选择器需要传递 int ，表示选择了 range 中的第几个 (下标从 0 开始)
        * time 时间选择器需要传递 str，表示选中的时间，格式为 "hh:mm"，如 "9:27"
        * date 日期选择器需要传递 str，表示选中的日期，格式为"YYYY-MM-DD"，如 "2020-07-07"

        [ 必要参数 ]
        * value (int or str) : 选择器取值

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].pick(value)
            self._log_output(f'选择器选值 -> [{ value }]', log)

            return self

        except BaseException as e:
            self._err_output(f'选择器选值异常::{ e }')


class _MiniPlantElementMapBase(object):
    """
    [ WEB元素控件封装基类 ]
    * 无

    """

    _mini_engine: MiniEngine
    """ [ 引擎对象 ] """

    _element_container: list = []
    """ [ 元素列表容器 ] """

    _analytical_elements = None
    """ [ 解析函数 ] """

    _log_output = None
    """ [ 日志输出函数 ] """

    _err_output = None
    """ [ 错误输出函数 ] """

    def __init__(self, mini_engine: MiniEngine,
                 analytical_elements_function,
                 log_output_function,
                 err_output_function):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * mini_engine (MiniEngine) : 小程序引擎对象
        * analytical_elements_function (function): 元素解析函数
        * log_output_function (function): 日志输出函数
        * err_output_function (function): 错误输出函数

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._web_engine = mini_engine
        self._analytical_elements = analytical_elements_function
        self._log_output = log_output_function
        self._err_output = err_output_function


class _MiniPlantElementMapGet(_MiniPlantElementMapBase):
    """
    [ 小程序元素控件'获取'相关函数 ]
    * 无

    """

    def count(self, log: bool = True) -> int:
        """
        [ 获取元素数量 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (int) : 元素数量

        """

        try:
            self._element_container = self._analytical_elements()

            count = len(self._element_container)
            self._log_output(f'获取元素列表数量[{ count }]', log)

            return count

        except BaseException as e:
            self._err_output(f'获取元素列表数量异常:: { e }')

    def text(self, eid: int = 0, log: bool = True) -> str:
        """
        [ 获取文本 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 元素文本

        """

        try:
            self._element_container = self._analytical_elements()

            text = self._element_container[eid].inner_text
            self._log_output(f'获取文本[{ text }]', log)

            return text

        except BaseException as e:
            self._err_output(f'获取文本异常:: { e }')

    def value(self, eid: int = 0, value_name: str = 'value', log: bool = True) -> str:
        """
        [ 获取属性值 ]
        * 获取元素名为 value_name 的属性值。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * value_name (str) : 获取属性的值名称
        * log (bool): 日志开关

        [ 返回内容 ]
        * (str) : 元素的属性值

        """

        try:
            self._element_container = self._analytical_elements()

            values = self._element_container[eid].attribute(value_name)
            self._log_output(f'获取属性值[{ values }]', log)

            return values

        except BaseException as e:
            self._err_output(f'获取属性值异常:: { e }')

    def styles(self, names: str or list, eid: int = 0, log: bool = True) -> str:
        """
        [ 获取样式属性 ]
        * 获取元素名为 names 的样式属性。

        [ 必要参数 ]
        * names (str or list) : 需要获取的 style 属性名称

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 元素的样式属性值

        """

        try:
            self._element_container = self._analytical_elements()

            values = self._element_container[eid].styles(names)
            self._log_output(f'获取样式属性[{ values }]', log)

            return values

        except BaseException as e:
            self._err_output(f'获取样式属性异常:: { e }')

    def in_page(self, eid: int = 0, wait: int = 3, log: bool = True):
        """
        [ 判断元素是否存在当前可视页面 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * wait (int) : 查找元素所等待的显式等待时长
        * log (bool) : 日志开关

        [ 返回参数 ]
        * (bool) : 布尔值

        """

        try:
            self._element_container = self._analytical_elements(wait=wait)

            proof = False
            practical_id = eid + 1

            if len(self._element_container) >= practical_id:
                proof = True

            self._log_output(f'判断元素是否存在当前可视页面[{ proof }]', log)

            return proof

        except BaseException as e:
            self._err_output(f'判断元素是否存在当前可视页面异常:: { e }')


class _MiniPlantElementMapMouse(_MiniPlantElementMapBase):
    """
    [ 小程序元素控件'鼠标'相关函数 ]
    * 无

    """

    def tap(self, eid: int = 0, log: bool = True):
        """
        [ 左键点击 ]
        * 模拟一次作用于元素对象上的鼠标左键单击操作。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回参数 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].tap()
            self._log_output('执行[左键点击]', log)

            return self

        except BaseException as e:
            self._err_output(f'执行[左键点击]异常:: { e }')

    def long_tap(self, eid: int = 0, duration: int = 1000, log: bool = True):
        """
        [ 左键长按 ]
        * 模拟一次作用于元素对象上的鼠标左键长按操作。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * duration (int) : 长按时长，单位是毫秒，默认为 1000
        * log (bool) : 日志开关

        [ 返回参数 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].long_press(duration)
            self._log_output('执行[左键长按]', log)

            return self

        except BaseException as e:
            self._err_output(f'执行[左键长按]异常:: { e }')

    def move(self,
             x_offset: int,
             y_offset: int,
             move_delay: int = 500,
             smooth: bool = False,
             eid: int = 0,
             log: bool = True):
        """
        [ 鼠标拖动 ]
        * 模拟一次作用于元素对象上的鼠标拖动操作。

        [ 必要参数 ]
        * x_offset (int) : x 方向上的偏移，往右为正数，往左为负数
        * y_offset (int) : y 方向上的偏移，往右为正数，往左为负数

        [ 可选参数 ]
        * move_delay (int) : 移动前摇，单位为毫秒，默认为 500
        * smooth (bool) : 平滑移动，默认为 False
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回参数 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].move_to(
                x_offset=x_offset,
                y_offset=y_offset,
                move_delay=move_delay,
                smooth=smooth
            )

            self._log_output('执行[鼠标拖动]', log)

            return self

        except BaseException as e:
            self._err_output(f'执行[鼠标拖动]异常:: { e }')


class _MiniPlantElementMapInput(_MiniPlantElementMapBase):
    """
    [ 小程序元素控件'输入框'相关函数 ]
    * 无

    """

    def send(self, key: str, eid: int = 0, log: bool = True):
        """
        [ 输入内容 ]
        * 输入内容，一般指向 input & textarea 组件。

        [ 必要参数 ]
        * key (str) : 内容文本

        [ 可选参数 ]
        * eid (int) : 指定元素下标，默认为 0
        * log (bool) : 日志开关

        [ 返回参数 ]
        * 无

        """

        try:
            self._element_container = self._analytical_elements()

            self._element_container[eid].input(key)
            self._log_output(f'输入文本[{ key }]', log)

            return self

        except BaseException as e:
            self._err_output(f'输入文本异常:: { e }')
