# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select

from rains.common.log import Log
from rains.common.task.case_recorder import CaseRecorder

from rains.kit.web.web_engine import WebEngine
from rains.kit.web.packaging.web_element_structure import WebElementStructure


class WebPlantElement(object):
    """
    WEB元素控件

    * 基于元素特征构建指向该元素的元素控件对象。

    """

    _log = Log()
    """ 日志服务 """

    _web_engine: WebEngine
    """ 引擎对象 """

    _case_recorder: CaseRecorder = CaseRecorder()
    """ 用例记录器 """

    _element_structure: WebElementStructure
    """ 元素结构体 """

    _element_container: list = []
    """ 元素列表容器 """

    def __init__(self, engine: WebEngine, element_structure: WebElementStructure):
        """
        初始化

        Args:
            engine (WebEngine): WEB引擎对象
            element_structure (WebElementStructure): WEB元素结构体

        """
        self._web_engine = engine
        self._element_structure = element_structure

    @property
    def get(self):
        """
        WEB元素控件'获取'相关函数
        """
        return _WebPlantElementMapGet(self._web_engine, self._analytical_elements, self._log_out, self._err_out)

    @property
    def mouse(self):
        """
        WEB元素控件'鼠标'相关函数
        """
        return _WebPlantElementMapMouse(self._web_engine, self._analytical_elements, self._log_out, self._err_out)

    @property
    def input(self):
        """
        WEB元素控件'输入框'相关函数
        """
        return _WebPlantElementMapInput(self._web_engine, self._analytical_elements, self._log_out, self._err_out)

    @property
    def selector(self):
        """
        WEB元素控件'下拉框'相关函数
        """
        return _WebPlantElementMapSelector(self._web_engine, self._analytical_elements, self._log_out, self._err_out)

    def _log_out(self, message: str, log: bool):
        """
        日志输出

        Args:
            message (str): 输出信息

        """
        if log:
            message = f'执行核心[{ self._web_engine.core_id }]::' \
                      f'{ self._element_structure.page }::' \
                      f'{ self._element_structure.name }::' \
                      f'{ message }'

            self._log.info(message)
            self._case_recorder.write(self._web_engine.core_id, message)

            return message

    def _err_out(self, message: str):
        """
        错误输出

        Args:
            message (str): 输出信息

        """
        message = self._log_out(message, True)
        raise Exception(message)

    def _analytical_elements(self, wait: int = 15, tolerance: bool = False) -> list:
        """
        解析函数

        * 每一次调用页面元素组件的方法时，都会调用该函数，以更新定位结果，确认组件是否存在于当前页面中。

        Args:
            wait (int): 查找元素所等待的显式等待时长
            tolerance (bool): 容错模式，为 True 则表示定位不到元素也不报错，返回空列表

        Return:
            元素列表容器

        """
        self._element_container = \
            self._web_engine.find_handle.find(self._element_structure, wait, tolerance)

        return self._element_container


class _WebPlantElementMapBase(object):
    """
    WEB元素控件封装基类
    """

    _web_engine: WebEngine
    """ 引擎对象 """

    _element_container: list = []
    """ 元素列表容器 """

    _analytical_elements = None
    """ 解析函数 """

    _log_out = None
    """ 日志输出函数 """

    _err_out = None
    """ 错误输出函数 """

    def __init__(self, web_element: WebEngine, analytical_elements_function, log_output_function, err_output_function):
        """
        初始化

        Args:
            web_element (WebEngine): WEB引擎对象
            analytical_elements_function (): 元素解析函数
            log_output_function (): 日志输出函数
            err_output_function (): 错误输出函数

        """
        self._web_engine = web_element
        self._analytical_elements = analytical_elements_function
        self._log_out = log_output_function
        self._err_out = err_output_function


class _WebPlantElementMapGet(_WebPlantElementMapBase):
    """
    WEB元素控件'获取'相关函数
    """

    def count(self, log: bool = True) -> int:
        """
        获取元素数量
        
        * 定位元素并且返回元素数量。

        Args:
            log (bool): 日志开关

        Return:
            元素数量

        """
        try:
            self._element_container = self._analytical_elements()
            count = len(self._element_container)
            self._log_out(f'获取元素列表数量[{ count }]', log)
            return count

        except BaseException as e:
            self._err_out(f'获取元素列表数量异常:: { e }')

    def text(self, eid: int = 0, log: bool = True) -> str:
        """
        获取文本

        * 返回元素的 text 属性值。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        Return:
            元素文本

        """
        try:
            self._element_container = self._analytical_elements()
            text = self._element_container[eid].text
            self._log_out(f'获取文本[{ text }]', log)
            return text

        except BaseException as e:
            self._err_out(f'获取文本异常:: { e }')

    def value(self, eid: int = 0, log: bool = True) -> str:
        """
        获取 value 值

        * 返回元素的 value 属性值。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        Return:
            元素的值

        """
        try:
            self._element_container = self._analytical_elements()
            value = self._element_container[eid].get_attribute('value')
            self._log_out(f'获取 value 值[{ value }]', log)
            return value

        except BaseException as e:
            self._err_out(f'获取 value 值异常:: { e }')

    def in_page(self, eid: int = 0, wait: int = 3, log: bool = True) -> bool:
        """
        判断元素是否存在当前可视页面

        Args:
            eid (int): 指定元素下标，默认为 0
            wait (int): 查找元素所等待的显式等待时长
            log (bool): 日志开关

        Return:
            Bool

        """
        try:
            self._element_container = self._analytical_elements(wait=wait, tolerance=True)

            proof = False
            if len(self._element_container) >= (eid + 1):
                proof = True
            self._log_out(f'判断元素是否存在当前可视页面[{ proof }]', log)

            return proof

        except BaseException as e:
            self._err_out(f'判断元素是否存在当前可视页面异常:: { e }')


class _WebPlantElementMapMouse(_WebPlantElementMapBase):
    """
    WEB元素控件'鼠标'相关函数
    """

    def tap(self, eid: int = 0, log: bool = True):
        """
        左键点击

        * 模拟一次作用于 WebElement 对象上的鼠标左键单击操作。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            ActionChains(self._web_engine.driver).click(self._element_container[eid]).perform()
            self._log_out('执行[左键点击]', log)
            return self

        except BaseException as e:
            self._err_out(f'执行[左键点击]异常:: { e }')

    def double_tap(self, eid: int = 0, log: bool = True):
        """
        左键双击

        * 模拟一次作用于 WebElement 对象上的鼠标左键双击操作。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            ActionChains(self._web_engine.driver).double_click(self._element_container[eid]).perform()
            self._log_out('执行[左键双击]', log)
            return self

        except BaseException as e:
            self._err_out(f'执行[左键双击]异常:: { e }')

    def long_tap(self, eid: int = 0, sleep: int = 2, log: bool = True):
        """
        左键长按

        * 模拟一次作用于 WebElement 对象上的鼠标左键长按操作。

        Args:
            eid (int): 指定元素下标，默认为 0
            sleep (int): 长按时长，默认为 2s
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            ActionChains(self._web_engine.driver).click_and_hold(self._element_container[eid]).perform()
            time.sleep(sleep)
            ActionChains(self._web_engine.driver).release(self._element_container[eid]).perform()
            self._log_out('执行[左键长按]', log)
            return self

        except BaseException as e:
            self._err_out(f'执行[左键长按]异常:: { e }')

    def move_to(self, eid: int = 0, log: bool = True):
        """
        鼠标悬停

        * 模拟一次作用于 WebElement 对象上的鼠标悬停操作。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            ActionChains(self._web_engine.driver).move_to_element(self._element_container[eid]).perform()
            self._log_out('执行[鼠标悬停]', log)
            return self

        except BaseException as e:
            self._err_out(f'执行[鼠标悬停]异常:: { e }')


class _WebPlantElementMapInput(_WebPlantElementMapBase):
    """
    WEB元素控件'输入框'相关函数
    """

    def send(self, key: str, eid: int = 0, log: bool = True):
        """
        输入内容

        * 输入内容，一般指向 input 标签组件。

        Args:
            key (str): 内容文本
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            self._element_container[eid].clear()
            self._element_container[eid].send_keys(key)
            self._log_out(f'输入文本[{ key }]', log)
            return self

        except BaseException as e:
            self._err_out(f'输入文本异常:: { e }')

    def clear(self, eid: int = 0, log: bool = True):
        """
        清除内容

        * 清除内容，一般指向 input 标签组件。

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._element_container = self._analytical_elements()
            self._element_container[eid].clear()
            self._log_out(f'清除输入框文本', log)
            return self

        except BaseException as e:
            self._err_out(f'清除输入框文本异常:: { e }')


class _WebPlantElementMapSelector(_WebPlantElementMapBase):
    """
    WEB元素控件'下拉框'相关函数
    """

    _select_handle: Select
    """ 下拉框处理器 """

    def __init__(self, web_element: WebEngine, analytical_elements_function, log_output_function, err_output_function):
        """
        初始化

        Args:
            web_element (WebEngine): WEB引擎对象
            analytical_elements_function (): 元素解析函数
            log_output_function (): 日志输出函数
            err_output_function (): 错误输出函数

        """
        super(_WebPlantElementMapSelector, self).__init__(web_element,
                                                          analytical_elements_function,
                                                          log_output_function,
                                                          err_output_function)

    def get_option_all_item(self, eid: int = 0, log: bool = True) -> list:
        """
        获取下拉框中所有的选项文本

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        Return:
            包含下拉框中所有的选项文本的列表

        """
        try:
            self._init_select_handle(eid)

            texts = []
            option_list = self._select_handle.options
            for i in option_list:
                texts.append(i.text)

            self._log_out(f'获取所有的选项文本', log)
            return texts

        except BaseException as e:
            self._err_out(f'获取所有的选项文本:: { e }')

    def get_option_all_select_item(self, eid: int = 0, log: bool = True) -> list:
        """
        获取下拉框中所有的已选中选项文本

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        Return:
            包含下拉框中所有的已选中选项文本的列表

        """
        try:
            self._init_select_handle(eid)

            texts = []
            option_list = self._select_handle.all_selected_options
            for i in option_list:
                texts.append(i.text)

            self._log_out(f'获取所有的已选中选项文本', log)
            return texts

        except BaseException as e:
            self._err_out(f'获取所有的已选中选项文本:: { e }')

    def get_option_current_item(self, eid: int = 0, log: bool = True):
        """
        获取下拉框中当前选择的首个选项文本

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        Return:
            下拉框中当前选择的首个选项文本

        """
        try:
            self._init_select_handle(eid)
            text = self._select_handle.first_selected_option.text
            self._log_out(f'获取当前选择的首个选项文本[{ text }]', log)
            return text

        except BaseException as e:
            self._err_out(f'获取当前选择的首个选项文本:: { e }')

    def select_by_index(self, index: int, eid: int = 0, log: bool = True):
        """
        下拉框中通过下标选择选项

        Args:
            index (int): 需要选中的选项下标
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_index(index)
            select_option_text = self._select_handle.first_selected_option.text
            self._log_out(f'通过下标选择选项[{ select_option_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过下标选择选项:: { e }')

    def select_by_value(self, value: str, eid: int = 0, log: bool = True):
        """
        下拉框中通过选项标签属性值选择

        Args:
            value (str): 需要选中的选项标签属性值
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_value(value)
            select_item_text = self._select_handle.first_selected_option.text
            self._log_out(f'通过标签属性值选择选项[{ select_item_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过标签属性值选择选项:: { e }')

    def select_by_text(self, text: str, eid: int = 0, log: bool = True):
        """
        下拉框中通过选项的文本选择

        Args:
            text (str): 需要选中的选项文本
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_visible_text(text)
            select_item_text = self._select_handle.first_selected_option.text
            self._log_out(f'通过选项的文本选择[{ select_item_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过选项的文本选择:: { e }')

    def deselect_all(self, eid: int = 0, log: bool = True):
        """
        下拉框中取消所有的已选中选项

        Args:
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.deselect_all()
            self._log_out(f'取消所有的已选中选项', log)
            return self

        except BaseException as e:
            self._err_out(f'取消所有的已选中选项:: { e }')

    def deselect_by_index(self, index: int, eid: int = 0, log: bool = True):
        """
        下拉框中通过下标取消已选中选项

        Args:
            index (int): 需要取消选中的选项下标
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_index(index)
            select_option_text = self._select_handle.first_selected_option.text
            self._select_handle.deselect_by_index(index)
            self._log_out(f'通过下标取消已选中选项[{ select_option_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过下标取消已选中选项:: { e }')

    def deselect_by_value(self, value: str, eid: int = 0, log: bool = True):
        """
        下拉框中通过选项标签属性值取消已选中选项

        Args:
            value (int): 需要取消选中的选项标签属性值
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_value(value)
            select_item_text = self._select_handle.first_selected_option.text
            self._select_handle.deselect_by_value(value)
            self._log_out(f'通过选项标签属性值取消已选中选项[{ select_item_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过选项标签属性值取消已选中选项:: { e }')

    def deselect_by_text(self, text: str, eid: int = 0, log: bool = True):
        """
        下拉框中通过选项的文本取消已选中选项

        Args:
            text (int): 需要取消选中的选项的文本
            eid (int): 指定元素下标，默认为 0
            log (bool): 日志开关

        """
        try:
            self._init_select_handle(eid)
            self._select_handle.select_by_visible_text(text)
            select_item_text = self._select_handle.first_selected_option.text
            self._select_handle.deselect_by_visible_text(text)
            self._log_out(f'通过选项的文本取消已选中选项[{ select_item_text }]', log)
            return self

        except BaseException as e:
            self._err_out(f'通过选项的文本取消已选中选项::{ e }')

    def _init_select_handle(self, eid):
        """
        初始化下拉框处理器

        Args:
            eid (int): 指定元素下标

        """
        self._element_container = self._analytical_elements()
        self._select_handle = Select(self._element_container[eid])
