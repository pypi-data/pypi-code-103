# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


import time
import win32con
import win32gui

from selenium.common.exceptions import InvalidArgumentException

from rains.common.log import Log
from rains.common.task.case_recorder import CaseRecorder

from rains.kit.web.web_engine import WebEngine


class WebPlantView(object):
    """
    WEB视图

    * 提供针对浏览器本身的操作函数。

    """

    _log = Log()
    """ 日志服务 """

    _engine: WebEngine
    """ 引擎对象 """

    _case_recorder: CaseRecorder = CaseRecorder()
    """ 用例记录器 """

    def __init__(self, engine: WebEngine):
        """
        [ 初始化 ]

        Args:
            engine (WebEngine): WEB引擎对象

        """
        self._engine = engine

    @property
    def get(self):
        """
        WEB视图'获取'相关函数
        """
        return _WebPlantViewMapGet(self._engine, self._log_out, self._err_out)

    @property
    def set(self):
        """
        WEB视图'设置'相关函数
        """
        return _WebPlantViewMapSet(self._engine, self._log_out, self._err_out)

    @property
    def page(self):
        """
        WEB视图'页面'相关函数
        """
        return _WebPlantViewMapPage(self._engine, self._log_out, self._err_out)

    @property
    def alert(self):
        """
        WEB视图'弹窗'相关函数
        """
        return _WebPlantViewMapAlert(self._engine, self._log_out, self._err_out)

    def to_url(self, url: str, log: bool = True):
        """
        跳转URL

        * 跳转至指定的URL。

        Args:
            url (str): URL
            log (bool): 日志开关

        """
        try:
            self._engine.driver.get(url)
            self._log_out(f'跳转URL[{ url }]', log)
            return self

        except InvalidArgumentException:
            self._err_out(f'跳转URL异常:: URL参数可能错误!')

        except BaseException as e:
            self._err_out(f'跳转URL异常:: { e }')

    def refresh(self, log: bool = True):
        """
        刷新页面

        * 当前标签页刷新页面。

        Args:
            log (bool): 日志开关

        """
        try:
            self._engine.driver.refresh()
            self._log_out(f'刷新页面', log)
            return self

        except BaseException as e:
            self._err_out(f'刷新页面异常:: { e }')

    def back(self, log: bool = True):
        """
        回退页面

        * 当前标签页回退页面。

        Args:
            log (bool): 日志开关

        """
        try:
            self._engine.driver.back()
            self._log_out(f'回退页面', log)
            return self

        except BaseException as e:
            self._err_out(f'回退页面异常:: { e }')

    def forward(self, log: bool = True):
        """
        前滚页面

        * 当前标签页前滚页面。

        Args:
            log (bool): 日志开关

        """
        try:
            self._engine.driver.forward()
            self._log_out(f'前滚页面', log)
            return self

        except BaseException as e:
            self._err_out(f'前滚页面异常::{ e }')

    def save_png(self, save_path: str, log: bool = True):
        """
        保存快照

        * 将当前浏览器截图保存至 save_path 中。

        Args:
            save_path (str): 保存 .png 的路径
            log (bool): 日志开关

        """
        try:
            self._engine.driver.get_screenshot_as_file(str(save_path))
            self._log_out(f'保存快照[{save_path}]', log)
            return self

        except BaseException as e:
            self._err_out(f'保存快照异常::{ e }')

    def upload_local_file(self, file_path: str, log: bool = True):
        """
        上传本地文件

        Args:
            file_path (str): 本地文件路径
            log (bool): 日志开关

        """
        try:
            # 打开 upload 对话框需要耗时
            time.sleep(1.5)

            # 获取 upload 对话框
            dialog = win32gui.FindWindow('#32770', u'打开')

            # 定位路径输入框与确认按钮的对象句柄
            combobox_ex32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
            combobox = win32gui.FindWindowEx(combobox_ex32, 0, 'ComboBox', None)
            edit = win32gui.FindWindowEx(combobox, 0, 'Edit', None)
            confirm_button = win32gui.FindWindowEx(dialog, 0, 'Button', None)

            # 调用句柄
            win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, file_path)
            win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, confirm_button)

            self._log_out(f'上传本地文件', log)
            return self

        except BaseException as e:
            self._err_out(f'上传本地文件异常:: { e }')

    def _log_out(self, message: str, log: bool):
        """
        日志输出

        Args:
            message (str): 输出信息

        """
        if log:
            message = f'执行核心[{ self._engine.core_id }]::{ message }'
            self._log.info(message)
            self._case_recorder.write(self._engine.core_id, message)

        return message

    def _err_out(self, message: str):
        """
        错误输出

        Args:
            message (str): 输出信息

        """
        message = self._log_out(message, True)
        raise Exception(message)


class _WebPlantViewMapBase(object):
    """
    WEB视图封装基类
    """

    _web_engine: WebEngine
    """ 引擎对象 """

    _log_out = None
    """ 日志输出函数 """

    _err_out = None
    """ 错误输出函数 """

    def __init__(self, web_engine: WebEngine, log_output_function, err_output_function):
        """
        [ 初始化 ]

        Args:
            web_engine (WebEngine): WEB引擎对象
            log_output_function (): 日志输出函数
            err_output_function (): 错误输出函数

        """
        self._web_engine = web_engine
        self._log_out = log_output_function
        self._err_out = err_output_function


class _WebPlantViewMapGet(_WebPlantViewMapBase):
    """
    WEB视图'获取'相关函数
    """

    def url(self, log: bool = True) -> str:
        """
        获取当前标签页的URL

        Args:
            log (bool): 日志开关

        """
        try:
            current_url = self._web_engine.driver.current_url
            self._log_out(f'获取当前标签页的URL[{ current_url }]', log)
            return current_url

        except BaseException as e:
            self._err_out(f'获取当前标签页的URL异常:: { e }')

    def title(self, log: bool = True) -> str:
        """
        获取当前标签页的 Title

        Args:
            log (bool): 日志开关

        """
        try:
            current_title = self._web_engine.driver.title
            self._log_out(f'当前标签页的 Title [{ current_title }]', log)
            return current_title

        except BaseException as e:
            self._err_out(f'当前标签页的 Title 异常:: { e }')

    def window_list(self, log: bool = True):
        """
        获取标签页句柄列表

        Args:
            log (bool): 日志开关

        """
        try:
            window_handles = self._web_engine.driver.window_handles
            self._log_out(f'获取标签页句柄列表', log)
            return window_handles

        except BaseException as e:
            self._err_out(f'获取标签页句柄列表异常:: { e }')

    def window_current(self, log: bool = True):
        """
        获取当前标签页句柄

        Args:
            log (bool): 日志开关

        """
        try:
            current_window_handle = self._web_engine.driver.current_window_handle
            self._log_out(f'获取当前标签页句柄[{ current_window_handle }]', log)
            return current_window_handle

        except BaseException as e:
            self._err_out(f'获取当前标签页句柄异常:: { e }')

    def browser_size(self, log: bool = True) -> dict:
        """
        获取浏览器尺寸

        Args:
            log (bool): 日志开关

        Return:
            标识浏览器尺寸信息的字典

        """
        try:
            browser_size = self._web_engine.driver.get_window_size()
            self._log_out(f'获取浏览器尺寸[{ browser_size }]', log)
            return browser_size

        except BaseException as e:
            self._err_out(f'获取浏览器尺寸异常:: { e }')

    def browser_position(self, log: bool = True) -> dict:
        """
        获取浏览器位置坐标

        Args:
            log (bool): 日志开关

        Return:
            标识浏览器位置坐标信息的字典

        """
        try:
            browser_position = self._web_engine.driver.get_window_position()
            self._log_out(f'获取浏览器位置坐标[{ browser_position }]', log)
            return browser_position

        except BaseException as e:
            self._err_out(f'获取浏览器位置坐标异常:: { e }')

    def cookies(self, log: bool = True) -> list:
        """
        获取 cookies

        Args:
            log (bool): 日志开关

        Return:
            cookies 列表

        """
        try:
            cookies = self._web_engine.driver.get_cookies()
            self._log_out(f'获取cookies', log)
            return cookies

        except BaseException as e:
            self._err_out(f'获取cookies异常:: { e }')


class _WebPlantViewMapSet(_WebPlantViewMapBase):
    """
    WEB视图'设置'相关函数
    """

    def browser_size(self, width: int, height: int, log: bool = True):
        """
        设置浏览器尺寸

        Args:
            width (int): 宽度
            height (int): 高度
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.set_window_size(width, height)
            self._log_out(f'设置浏览器尺寸[{ width }::{ height }]', log)
            return self

        except BaseException as e:
            self._err_out(f'设置浏览器尺寸异常:: { e }')

    def browser_position(self, x: int, y: int, log: bool = True):
        """
        设置浏览器位置坐标

        Args:
            x (int): x坐标
            y (int): y坐标
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.set_window_position(x, y)
            self._log_out(f'设置浏览器位置坐标[{ x }::{ y }]', log)
            return self

        except BaseException as e:
            self._err_out(f'设置浏览器位置坐标异常:: { e }')

    def browser_max(self, log: bool = True):
        """
        设置浏览器窗口最大化

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.maximize_window()
            self._log_out(f'设置浏览器窗口最大化', log)
            return self

        except BaseException as e:
            self._err_out(f'设置浏览器窗口最大化异常:: { e }')

    def browser_min(self, log: bool = True):
        """
        设置浏览器窗口最小化

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.minimize_window()
            self._log_out(f'设置浏览器窗口最小化', log)
            return self

        except BaseException as e:
            self._err_out(f'设置浏览器窗口最小化异常:: { e }')

    def del_cookies(self, log: bool = True):
        """
        删除 cookies

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.delete_all_cookies()
            self._log_out(f'删除cookies', log)
            return self

        except BaseException as e:
            self._err_out(f'删除cookies异常:: { e }')

    def add_cookies(self, cookie_list: list, log: bool = True):
        """
        添加 cookies

        Args:
            cookie_list (list): cookies 列表
            log (bool): 日志开关

        """
        try:
            for i in cookie_list:
                self._web_engine.driver.add_cookie(i)

            self._log_out(f'设置cookies', log)
            return self

        except BaseException as e:
            self._err_out(f'设置cookies异常:: { e }')


class _WebPlantViewMapPage(_WebPlantViewMapBase):
    """
    WEB视图'页面'相关函数
    """

    def open(self, url: str = '', log: bool = True):
        """
        打开新的标签页

        * 在当前浏览器中, 打开一个新的标签页。

        Args:
            url (str): 新标签页的URL，默认为空
            log (bool): 日志开关

        """
        try:
            # 通过JS语句打开新标签页
            self._web_engine.driver.execute_script(f'window.open("{url}")')
            # 将当前句柄跳转至新标签页
            self._web_engine.driver.switch_to.window(self._web_engine.driver.window_handles[-1])
            self._log_out(f'打开新标签页[{ len(self._web_engine.driver.window_handles) - 1 }]->[{ url }]', log)
            return self

        except BaseException as e:
            self._err_out(f'打开新标签页异常:: { e }')

    def switch(self, number: int, log: bool = True):
        """
        切换至标签页

        * 在当前浏览器中, 切换至编号为 [number] 的已存在标签页。

        Args:
            number (str): 标签页编号
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.switch_to.window(self._web_engine.driver.window_handles[number])
            self._log_out(f'切换至标签页[{ number }]', log)
            return self

        except IndexError:
            self._err_out(f'切换至标签页异常:: 没有这样的标签页，请重新确认标签页编号！')

        except BaseException as e:
            self._err_out(f'切换至标签页异常:: { e }')

    def close(self, number: int, log: bool = True):
        """
        关闭标签页

        * 在当前浏览器中, 关闭编号为 [number] 的已存在标签页。

        Args:
            number (str): 标签页编号
            log (bool): 日志开关

        """
        try:
            if len(self._web_engine.driver.window_handles) > 1:
                self.switch(number, log=False)
                self._web_engine.driver.close()
                self._web_engine.driver.switch_to.window(self._web_engine.driver.window_handles[-1])
                self._log_out(f'关闭标签页[{ number }]', log)
                return self

        except IndexError:
            self._err_out(f'切换至标签页异常:: 没有这样的标签页，请重新确认标签页编号！')

        except BaseException as e:
            self._err_out(f'切换至标签页异常:: { e }')

    def close_all(self, log: bool = True):
        """
        关闭所有标签页

        * 在当前浏览器中, 关闭所有已存在的标签页, 仅保留一个空白标签。

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.reset()
            self._log_out(f'关闭全部标签页', log)
            return self

        except BaseException as e:
            self._err_out(f'关闭全部标签页异常:: { e }')


class _WebPlantViewMapAlert(_WebPlantViewMapBase):
    """
    WEB视图'弹窗'相关函数
    """

    def get_text(self, log: bool = True) -> str:
        """
        获取弹窗文本

        Args:
            log (bool): 日志开关

        Return:
            弹窗文本字符串

        """
        try:
            alert_text = self._web_engine.driver.switch_to.alert.text
            self._log_out(f'获取弹窗文本[{ alert_text }]', log)
            return alert_text

        except BaseException as e:
            self._err_out(f'获取弹窗文本异常:: { e }')

    def tap_accept(self, log: bool = True):
        """
        点击弹窗确定按钮

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.switch_to.alert.accept()
            self._log_out(f'点击弹窗确定按钮', log)
            return self

        except BaseException as e:
            self._err_out(f'点击弹窗确定按钮异常:: { e }')

    def tap_dismiss(self, log: bool = True):
        """
        点击弹窗取消按钮

        Args:
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.switch_to.alert.dismiss()
            self._log_out(f'点击弹窗取消按钮', log)
            return self

        except BaseException as e:
            self._err_out(f'点击弹窗取消按钮异常:: { e }')

    def send_key(self, key: str, log: bool = True):
        """
        弹窗输入文本

        Args:
            key (str): 文本
            log (bool): 日志开关

        """
        try:
            self._web_engine.driver.switch_to.alert.send_keys(key)
            self._log_out(f'弹窗输入文本[{ key }]', log)
            return self

        except BaseException as e:
            self._err_out(f'弹窗输入文本异常:: { e }')
