# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['MiniPlantView']


from rains.common.log import Log

from rains.kit.mini.mini_engine import MiniEngine


class MiniPlantView(object):
    """
    [ 小程序视图 ]
    * 提供针对小程序本身的操作函数。

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

    def _log_output(self, message: str, log: bool):
        """
        [ 日志输出 ]
        * 无

        [ 必要参数 ]
        * message (str) : 输出信息

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if log:
            self._log.info(f'执行核心[{ self._mini_engine.id }]::{ message }')

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

        raise Exception(f'执行核心[{ self._mini_engine.id }]::{ message }')

    @property
    def get(self):
        """
        [ WEB视图'获取'相关函数 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        return _MiniPlantViewMapGet(self._mini_engine, self._log_output, self._err_output)

    @property
    def page(self):
        """
        [ WEB视图'获取'相关函数 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        return _MiniPlantViewMapPage(self._mini_engine, self._log_output, self._err_output)

    def save_png(self, save_path: str, log: bool = True):
        """
        [ 保存快照 ]
        * ide上仅能截取到 wxml 页面的内容，Modal/Actionsheet/授权弹窗等无法截取。

        [ 必要参数 ]
        * save_path (str) : 保存 .png 的路径

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._mini_engine.driver.app.screen_shot(str(save_path))
            self._log_output(f'保存快照[{ save_path }]', log)

            return self

        except BaseException as e:
            self._err_output(f'保存快照异常::{ e }')


class _MiniPlantViewMapBase(object):
    """
    [ 小程序视图封装基类 ]
    * 无

    """

    _mini_engine: MiniEngine
    """ [ 引擎对象 ] """

    _log_output = None
    """ [ 日志输出函数 ] """

    _err_output = None
    """ [ 错误输出函数 ] """

    def __init__(self, mini_engine: MiniEngine, log_output_function, err_output_function):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * mini_engine (MiniEngine) : 小程序引擎对象
        * log_output_function (function) : 日志输出函数
        * err_output_function (function) : 错误输出函数

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._mini_engine = mini_engine
        self._log_output = log_output_function
        self._err_output = err_output_function


class _MiniPlantViewMapGet(_MiniPlantViewMapBase):
    """
    [ 小程序视图'获取'相关函数 ]
    * 无

    """

    def data(self, log: bool = True) -> str:
        """
        [ 获取当前页面数据 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 当前页面数据

        """

        try:
            data = self._mini_engine.driver.app.get_current_page().data
            self._log_output('获取当前页面数据', log)

            return data

        except BaseException as e:
            self._err_output(f'获取当前页面数据异常:: { e }')

    # func boundary -----------------------------------------------------------------------------------------------

    def pages(self, log: bool = True) -> str:
        """
        [ 获取所有已配置的页面路径 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 当前页面数据

        """

        try:
            paths = self._mini_engine.driver.app.get_all_pages_path()
            self._log_output('获取所有已配置的页面路径', log)

            return paths

        except BaseException as e:
            self._err_output(f'获取所有已配置的页面路径异常:: { e }')

    # func boundary -----------------------------------------------------------------------------------------------

    def current_page(self, log: bool = True) -> str:
        """
        [ 获取当前顶层页面 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 当前页面数据

        """

        try:
            page = self._mini_engine.driver.app.get_current_page()
            path = page.path

            self._log_output(f'获取当前顶层页面[{ path }]', log)

            return path

        except BaseException as e:
            self._err_output(f'获取当前顶层页面异常:: { e }')


class _MiniPlantViewMapPage(_MiniPlantViewMapBase):
    """
    [ 小程序视图'页面'相关函数 ]
    * 无

    """

    def to_home(self, log: bool = True):
        """
        [ 跳转至小程序首页 ]
        * 无

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * log (bool) : 日志开关

        [ 返回内容 ]
        * (str) : 当前页面数据

        """

        try:
            self._mini_engine.driver.app.go_home()
            self._log_output('跳转至小程序首页', log)

            return self

        except BaseException as e:
            self._err_output(f'跳转至小程序首页异常:: { e }')

    def to_page(self, page_path: str, params: dict = None, is_wait: bool = True, log: bool = True):
        """
        [ 跳转页面 ]
        * 以导航的方式跳转到指定页面。
        * 不能跳到 tabBar 页面，支持相对路径和绝对路径，小程序中页面栈最多十层。
        * 页面路径规则：
        * /page/tabBar/API/index: 绝对路径,最前面为/。
        * tabBar/API/index: 相对路径, 会被拼接在当前页面父节点的路径后面。

        [ 必要参数 ]
        * page_path (str) : 页面路径

        [ 可选参数 ]
        * params (dict) : 页面参数
        * is_wait (bool) : 是否等待新的页面跳转
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._mini_engine.driver.app.navigate_to(page_path, params, is_wait)
            self._log_output(f'跳转至页面[{ page_path }]', log)

            return self

        except BaseException as e:
            self._err_output(f'跳转至页面异常:: { e }')

    def back(self, delta: int = 1, log: bool = True):
        """
        [ 返回页面 ]
        * 关闭当前页面，返回上一页面或多级页面。
        * 如果超出当前页面栈最大层数，返回首页。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * delta (int) : 返回的层数
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._mini_engine.driver.app.navigate_back(delta)
            self._log_output(f'返回上[{ delta }]层页面，', log)

            return self

        except BaseException as e:
            self._err_output(f'返回页面异常:: { e }')

    def switch_tab(self, tab_path: int = 1, log: bool = True):
        """
        [ 跳转至 tabBar 页面 ]
        * 会关闭其他所有非 tabBar 页面。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * tab_path (int) : 需要跳转的 tabBar 页面的路径（需在 app.json 的 tabBar 字段定义的页面），路径后不能带参数
        * log (bool) : 日志开关

        [ 返回内容 ]
        * 无

        """

        try:
            self._mini_engine.driver.app.switch_tab(tab_path)
            self._log_output(f'跳转至 tabBar 页面[{ tab_path }]，', log)

            return self

        except BaseException as e:
            self._err_output(f'跳转至 tabBar 页面异常:: { e }')
