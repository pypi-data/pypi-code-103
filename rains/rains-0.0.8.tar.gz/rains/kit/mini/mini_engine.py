# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['MiniEngine']


import minium

from minium import Minium

from rains.common.log import Log
from rains.common.const import ConstProjectType
from rains.common.i.i_engine import IEngine

from rains.kit.mini.packaging.mini_find_handle import MiniFindHandle


class MiniEngine(IEngine):
    """
    [ 小程序引擎 ]
    * 引擎封装了原生驱动的获取逻辑与小程序元素定位器，并且管理着驱动对象的生命周期。

    """

    _log = Log()
    """ WEB引擎 """

    _state: bool
    """ 状态 """

    _core_id: int
    """ 编号 """

    _type: str = ConstProjectType.MINI
    """ 类型 """

    _driver: Minium = None
    """ 原生驱动对象 """

    _find_handle: MiniFindHandle = None
    """ 元素定位器 """

    driver_config: dict = {

        # 小程序运行的平台，可选值为: ide, Android, IOS
        'platform': 'ide',

        # 日志打印级别，可选: error, warn, info, debug
        'debug_mode': 'error',

        # IDE监听的端口，默认为 9420
        'test_port': 9420,

        # 请求连接超时时间 s
        'request_timeout': 30,

        # 每个case启动的时候relaunch到启动页面
        'auto_relaunch': True,

        # 自动处理授权弹窗
        # 包括: 获取用户信息，获取位置，获取微信运动数据，获取录音权限，获取相册权限，获取摄像头权限
        'auto_authorize': False

    }
    """ 驱动配置 """

    def __init__(self, project_path: str, wx_cli_path: str, core_id: int):
        """
        [ 初始化 ]
        * 无

        [ 必要参数 ]
        * project_path (str) : 项目路径
        * wx_cli_path (str) : 微信开发者工具 cli.bat 的路径
        * core_id (int) : 核心ID，默认为空，不传则自动生成

        [ 可选参数 ]
        * 无

        [ 返回内容 ]
        * 小程序引擎对象

        """

        self.driver_config['project_path'] = project_path
        self.driver_config['dev_tool_path'] = wx_cli_path
        self._core_id = core_id
        self.state = False

    @property
    def core_id(self):
        return self._core_id

    @property
    def type(self):
        return self._type

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

        return self.state

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

        if not self.state:

            self._log.info('正在尝试建立"微信开发者工具"的服务端口连接...')

            self._driver = minium.Minium(self.driver_config)

            self._log.info('成功建立"微信开发者工具"的服务端口连接...')
            self._log.info(f'打印当前"微信开发者工具"的系统信息:: { self._driver.get_system_info() }')

            self._find_handle = MiniFindHandle(self._driver)
            self.state = True

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

        if self.state:

            self._driver.shutdown()

            del self._driver

            self.state = False

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

        if self.state:

            self._driver.app.go_home()

        return self
