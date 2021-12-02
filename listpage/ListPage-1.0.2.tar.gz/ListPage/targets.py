# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2020-11-17
# @email     : g1879@qq.com
# @File      : targets.py
from typing import Union

from .common import format_loc
from .paths import Paths


class Targets(object):
    """此类用于管理待爬取目标                                         \n
    待爬目标由一个3位的元组表示：(列名, [属性名, 正则表达式])              \n
    如：('作者', 'text', '(.*)')                                   \n
    其中后两位可省略，当省略时默认获取元素text值                          \n
    即传入'作者' 与传入 ('作者', 'text', '(.*)')是等价的               \n
    示例：                                                         \n
        - '作者'                                                   \n
        - '链接', 'href'                                           \n
        - '页数', 'text', '(\\d+)'                                 \n
    """

    def __init__(self,
                 paths: Union[Paths, dict],
                 targets: dict = None):
        """初始化                              \n
        :param paths: Paths对象或路径字典
        :param targets: 要爬取的内容字典
        """
        if isinstance(paths, Paths):
            self._paths = paths

        elif isinstance(paths, dict):
            self._paths = Paths(paths_dict=paths)

        else:
            raise TypeError('paths参数只能是Paths或dict类型。')

        self._targets = {}
        self._start_stop_row = (None, None)

        if targets:
            self.set_targets(targets)

    @property
    def paths(self) -> Paths:
        """返回页面路径管理对象"""
        return self._paths

    @property
    def start_stop_row(self) -> tuple:
        """返回起止行号"""
        return self._start_stop_row

    @start_stop_row.setter
    def start_stop_row(self, start_stop: Union[list, tuple]):
        """设置起止行号"""
        if not isinstance(start_stop, (list, tuple)) or not 0 < len(start_stop) < 3:
            raise ValueError

        self._start_stop_row = (start_stop[0], None) if len(start_stop) == 1 else start_stop

    @property
    def targets(self) -> dict:
        """返回所有目标组成的字典"""
        return self._targets

    @targets.setter
    def targets(self, targets: dict) -> None:
        """批量设置目标                            \n
        :param targets: 列表或元组格式的目标信息
        :return: None
        """
        self.set_targets(targets)

    def set_targets(self, targets: dict) -> None:
        """批量设置目标                            \n
        :param targets: 列表或元组格式的目标信息
        :return: None
        """
        if not isinstance(targets, dict):
            raise TypeError(f'请传入dict，不是{type(targets)}')

        # 有范围设置时
        s_s = targets.get('start_stop', None)
        if not s_s:
            self._start_stop_row = (None, None)
        elif isinstance(s_s, (list, tuple)) and isinstance(s_s[0], (int, type(None))):
            if not 0 < len(s_s) < 3:
                raise ValueError('start_stop元素个数应为1-2个。')

            self._start_stop_row = (s_s[0], None) if len(s_s) == 1 else s_s

        for name in targets:
            if name == 'start_stop':
                continue

            xpath_str, attr_str, re_str = format_loc(targets[name])
            self.add_target(name, xpath_str, attr_str, re_str)

    def add_target(self, name: str, col: str, attr: str = None, re_str: str = None) -> None:
        """添加待爬目标                                     \n
        :param name: 目标标题
        :param col: 已在 paths 中定义的列的名称
        :param attr: 要抓取的属性
        :param re_str: 提取属性内容的正则表达式
        :return: None
        """
        path_str = self.paths.cols[col]
        attr = attr or 'text'
        re_str = re_str or '(.*)'

        self._targets[name] = (path_str, attr, re_str)
