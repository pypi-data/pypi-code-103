# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


from selenium import webdriver
from selenium.webdriver.chrome.webdriver import RemoteWebDriver

from rains.common.log import Log
from rains.common.i.i_engine import IEngine
from rains.common.const import ConstProjectType

from rains.kit.web.packaging.web_find_handle import WebFindHandle
from rains.kit.web.web_const import BrowserType


class WebEngine(IEngine):
    """
    [ WEB引擎 ]
    * 引擎封装了原生驱动的获取逻辑与一个基于原生 Selenium3 二次实现的元素定位器，并且管理着驱动对象的生命周期。

    """

    _log = Log()
    """ WEB引擎 """

    _state: bool
    """ 状态 """

    _core_id: int
    """ 编号 """

    _type: str = ConstProjectType.WEB
    """ 类型 """

    _browser_type: str = BrowserType.CHROME
    """ 浏览器类型 """

    _driver: RemoteWebDriver = None
    """ 原生驱动对象 """

    _find_handle: WebFindHandle = None
    """ 元素定位器 """

    def __init__(self, core_id: int):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * core_id (int): 核心ID

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._core_id = core_id
        self._state = False

    @property
    def core_id(self):
        return self._core_id

    @property
    def type(self):
        return self._type

    @property
    def browser_type(self):
        return self.browser_type

    @property
    def driver(self):
        return self._driver

    @property
    def find_handle(self):
        return self._find_handle

    def get_state(self) -> bool:
        """
        [ 获取引擎状态 ]
        * 获取当前引擎状态，启动中返回 True，否则返回 False。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * (Bool) : 当前引擎状态

        """

        return self._state

    def set_browser_type(self, browser_type: str):
        """
        [ 设置浏览器类型 ]
        * 无

        [ 必要参数 ]
        * browser_type (str) : 浏览器类型

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        self._browser_type = browser_type
        return self

    def run(self):
        """
        [ 运行引擎 ]
        * 驱动与定位器的实例化。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if not self._state:

            # 谷歌浏览器
            if self._browser_type == BrowserType.CHROME:
                # 以非 W3C 模式运行
                # 不显示自动化劫持 && 不打印日志
                # 创建浏览器驱动实例
                opt = webdriver.ChromeOptions()
                opt.add_experimental_option('w3c', False)
                opt.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
                self._driver = webdriver.Chrome(options=opt)
                self._find_handle = WebFindHandle(self._driver)
                self._state = True

        return self

    def end(self):
        """
        [ 结束引擎 ]
        * 退出并销毁当前持有的驱动与定位器。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if self._state:

            self._driver.quit()
            self._state = False

            del self._driver
            del self._find_handle

            return self

    def reset(self):
        """
        [ 重置引擎 ]
        * 将引擎重置至初始阶段。
        * 与 end() 相比，该函数只是重置引擎至初始状态，而不是注销。

        [ 必要参数 ]
        * 无

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 无

        """

        if self._state:

            # 打开一个新空白标签页
            self._driver.execute_script(f'window.open("")')

            # 关闭所有其他标签页面
            new_page_handle = self._driver.window_handles[-1]

            for page_handle in self._driver.window_handles:
                if page_handle != new_page_handle:
                    self._driver.switch_to.window(page_handle)
                    self._driver.close()

            # 句柄回到新空白标签页
            self._driver.switch_to.window(new_page_handle)

        return self
