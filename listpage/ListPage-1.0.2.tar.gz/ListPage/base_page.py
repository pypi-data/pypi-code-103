# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2020-11-17
# @email     : g1879@qq.com
# @File      : base_page.py
from abc import abstractmethod
from re import search, DOTALL
from typing import Union, List

from DrissionPage import MixPage, Drission
from DrissionPage.driver_element import DriverElement
from DrissionPage.session_element import SessionElement

from .common import format_loc
from .paths import Paths
from .targets import Targets


class BasePage(MixPage):
    """列表页的基类"""

    def __init__(self,
                 paths: Union[Paths, dict],
                 index_url: str = None,
                 mode: str = 's',
                 timeout: float = 10,
                 drission: Drission = None):
        """初始化                                     \n
        :param paths: 页面元素管理对象或字典
        :param index_url: 列表第一页url
        :param mode: 's' 或 'd'，对应MixPage的模式
        :param timeout: 超时时间
        :param drission: Drission对象
        """
        super().__init__(drission=drission, mode=mode, timeout=timeout)
        self._set_paths(paths)
        self.index_url = index_url
        self._current_page_num = 1

        if index_url:
            self.to_first_page()

    @property
    def paths(self) -> Paths:
        """返回页面路径管理对象"""
        return self._paths

    def to_first_page(self) -> None:
        """跳转到首页"""
        if self.index_url:
            self.get(self.index_url, go_anyway=True, show_errmsg=True, retry=6, interval=10)
            self._current_page_num = 1
        else:
            raise ValueError('首页url未设置')

    def get_current_rows(self) -> Union[List[DriverElement], List[SessionElement]]:
        """返回当前页行对象"""
        return self.eles(f'{self.paths.type}:{self.paths.rows}')

    def get_current_list(self,
                         targets: Union[Targets, dict],
                         show_msg: bool = True) -> List[dict]:
        """返回当前页结果列表                      \n
        :param targets: 要爬取的目标对象或字典
        :param show_msg: 是否显示获取到的内容
        :return: 结果列表
        """
        rows = self.get_current_rows()
        return self._get_list(rows, targets, show_msg)

    @abstractmethod
    def get_list(self,
                 targets: Union[Targets, dict],
                 show_msg: bool = True,
                 wait: float = 0) -> List[dict]:
        """返回指定范围的结果列表，由子类实现                    \n
        :param targets: Targets对象
        :param show_msg: 是否实时显示获取到的内容
        :param wait: 每页之间等待时间
        :return: 结果列表
        """
        pass

    @abstractmethod
    def to_next_page(self, wait: float = None) -> bool:
        """跳转到下一页                    \n
        :param wait: 跳转前的等待时间
        :return: 是否跳转成功
        """
        pass

    def _get_list(self,
                  rows: list,
                  targets: Union[Targets, dict],
                  show_msg: bool = True) -> List[dict]:
        """从行对象列表中获取须要的属性值                    \n
        :param rows: 行对象组成的列表
        :param targets: Targets对象
        :param show_msg: 是否实时显示获取到的信息
        :return: 结果列表
        """
        if isinstance(targets, Targets):
            pass
        elif isinstance(targets, dict):
            targets = Targets(self.paths, targets)
        else:
            raise TypeError('targets参数只能是Targets或dict。')

        start, stop = targets.start_stop_row

        results_list = []
        for row in rows[start: stop]:
            row_result = {t: self._get_value(row, targets.targets[t], t, show_msg) for t in targets.targets}

            if show_msg:
                print(row_result)

            results_list.append(row_result)

        return results_list

    def _get_value(self,
                   ele_or_page: Union[MixPage, DriverElement, SessionElement],
                   loc: Union[str, list, tuple],
                   title: str,
                   show_msg: bool = True) -> Union[str, None]:
        """根据定位从元素中获取值                                    \n
        :param ele_or_page: 获取值的目标对象
        :param loc: 定位符：(xpath或css路径, [属性名, 正则])
        :param title: 要获取的数据标题
        :param show_msg: 获取不到数据时是否显示错误
        :return: 获取到的属性值
        """
        path_str, attr_str, re_str = format_loc(loc)

        try:
            data = ele_or_page.ele(f'{self.paths.type}:{path_str}', timeout=1).attr(attr_str)
            r = search(re_str, data, flags=DOTALL)
            return r.group(1)

        except AttributeError:
            if show_msg:
                print(f'\n找不到：{title}\n')
            return None

    def _set_paths(self, dict_or_Paths: Union[dict, Paths]) -> None:
        """设置路径对象                                 \n
        :param dict_or_Paths: Paths对象或dict
        :return: None
        """
        if isinstance(dict_or_Paths, Paths):
            self._paths = dict_or_Paths

        elif isinstance(dict_or_Paths, dict):
            self._paths = Paths(paths_dict=dict_or_Paths)

        else:
            raise ValueError('paths格式错误')
