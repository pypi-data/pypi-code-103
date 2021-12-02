# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2020-07-30
# @email     : g1879@qq.com
# @File      : list_page.py
from re import sub, search
from time import sleep
from typing import Union, List

from DataRecorder import Recorder
from DrissionPage import Drission

from .base_page import BasePage
from .paths import Paths
from .targets import Targets


class ListPage(BasePage):
    """列表页基类                                                    \n
    列表页基类提取了列表页面共有的特征，封装了对页面的基本读取和操作方法。
    """

    def __init__(self,
                 paths: Union[Paths, dict],
                 index_url: str = None,
                 mode: str = 's',
                 timeout: float = 10,
                 drission: Drission = None):
        """初始化函数                                       \n
        :param paths: 页面元素管理对象
        :param index_url: 列表第一页url
        :param mode: 's' 或 'd'，MixPage模式
        :param timeout: 超时时间
        :param drission: Drission对象
        """
        super().__init__(paths, index_url, mode, timeout, drission)
        self._pages_count = self._get_pages_count_from_paths()  # 列表总页数
        self._num_param = None  # url 中页码参数
        self.step = 1  # 翻页编码步长
        self.first_num = 1  # 第一页页码，0 或 1

    def __del__(self):
        print(f'\n当前页码：{self.current_page_num}')

    @property
    def current_page_num(self) -> int:
        """返回当前页码"""
        if self.num_param:
            self._current_page_num = self._get_page_num_from_url()

        return self._current_page_num

    @property
    def pages_count(self) -> Union[int, None]:
        """返回总页数"""
        return self._pages_count

    @pages_count.setter
    def pages_count(self, num: int) -> None:
        """手动设置总页数           \n
        :param num: 总页数
        :return: None
        """
        self._pages_count = num

    @property
    def num_param(self) -> str:
        """返回 url 中页码参数"""
        return self._num_param

    @num_param.setter
    def num_param(self, param: str) -> None:
        """设置 url 中页码参数            \n
        :param param: url 中页码参数
        :return: None
        """
        if not param.startswith('/') and f'{param}=' not in self.index_url:
            raise ValueError('要使用页码翻页，须在index_url中包含该参数')

        self._num_param = param

    def set_index_url(self, index_url: str) -> None:
        """设置新的页面，重新初始化对象
        :param index_url: 新的首页url
        :return: None
        """
        self._index_url = index_url
        self.to_first_page()
        self._pages_count = self._get_pages_count_from_paths()  # 列表总页数

    def get_list(self,
                 targets: Union[Targets, dict],
                 begin_page: int = None,
                 count: int = None,
                 stop_when_empty: bool = True,
                 wait: float = None,
                 show_msg: bool = True,
                 recorder: Recorder = None,
                 return_data: bool = True) -> List[dict]:
        """根据targets的内容爬取列表内容            \n
        :param targets: 要爬取的内容
        :param begin_page: 起始页码
        :param count: 爬取页面数量
        :param stop_when_empty: 空页是否停止
        :param wait: 翻页后等待几秒
        :param show_msg: 是否显示爬取信息
        :param recorder: 记录器对象
        :param return_data: 是否返回数据
        :return: 结果列表
        """
        if begin_page:
            self.to_page(begin_page)
        else:
            begin_page = self.current_page_num

        if not stop_when_empty:
            if not self.pages_count and not count:
                raise KeyError('须传入爬取页数')

            if count and (not isinstance(count, int) or count < 1):
                raise TypeError('count须传入正整数')

        # 获取要爬页数
        if self.pages_count and (not count or count > self.pages_count - begin_page + 1):
            count = self.pages_count - begin_page + 1

        data_list = []
        got_page = 0

        while True:
            if show_msg:
                print(f'\n第{begin_page + got_page}页')
                print(self.url)

            current_list = self.get_current_list(targets, show_msg=show_msg)

            if not current_list and stop_when_empty:
                if show_msg:
                    print('空列表，终止。')
                break

            if return_data:
                data_list.extend(current_list)

            if recorder:
                recorder.add_data(current_list)

            got_page += 1

            if count and count == got_page:
                break

            if not self.to_next_page(wait):
                break

        if recorder:
            recorder.record()

        return data_list

    def to_page(self, num: int, wait: float = None) -> None:
        """跳转到任意页                        \n
        :param num: 页码
        :param wait: 翻页后等待秒数
        :return: None
        """
        if self.num_param and self._to_page_by_num(num) is not False:
            self._current_page_num = num
            return

        else:

            if self.pages_count and not 0 < num <= self.pages_count:
                raise KeyError('始页应该在总页数范围内')

            if self.index_url:
                self.to_first_page()

                for _ in range(num - 1):
                    self.to_next_page(wait=wait)
            else:
                raise ValueError('首页url未设置')

    def to_next_page(self, wait: float = None) -> bool:
        """跳转到下一页                        \n
        :param wait: 跳转后等待秒数
        :return: 跳转是否成功
        """
        if self.num_param:
            current_num = self._get_page_num_from_url()
            is_ok = self._to_page_by_num(current_num + 1)

        else:
            next_btn = self.ele(f'{self.paths.type}:{self.paths.next_btn}', timeout=2)

            if next_btn:
                if self.mode == 's':
                    is_ok = self._to_next_s_mode()
                else:
                    is_ok = self._to_next_d_mode()
            else:
                is_ok = False

        if is_ok is not False:
            self._current_page_num += 1
            result = True
        else:
            result = False

        if wait:
            sleep(wait)

        return result

    def _to_next_s_mode(self) -> bool:
        """s模式下跳转到下一页的方法                       \n
        有必要时重载这个方法处理特殊的跳转规则
        """
        next_btn = self.ele(f'{self.paths.type}:{self.paths.next_btn}')

        if next_btn:
            return super().get(next_btn.attr('href'), go_anyway=True, show_errmsg=True)
        else:
            return False

    def _to_next_d_mode(self) -> bool:
        """d模式下跳转到下一页的方法                       \n
        有必要时重载这个方法处理特殊的跳转规则
        """
        next_btn = self.ele(f'{self.paths.type}:{self.paths.next_btn}', timeout=2)

        if next_btn:
            next_btn.click(by_js=True)
            sleep(.5)
            return True
        else:
            return False

    def _to_page_by_num(self, num: int, wait: float = None) -> Union[bool, None]:
        """根据页码跳转                        \n
        :param num: 页码
        :param wait: 跳转后等待秒数
        :return: 跳转后是否成功
        """
        if wait:
            sleep(wait)

        if not self.num_param:
            return False

        if self.num_param.startswith('/'):
            new_url = sub(f'{self.num_param}(\\d*)', f'{self.num_param}{self._page_num_to_url_num(num)}', self.url)
        else:
            new_url = sub(f'{self.num_param}=(\\d*)', f'{self.num_param}={self._page_num_to_url_num(num)}', self.url)

        return super().get(new_url, go_anyway=True, show_errmsg=True)

    def _get_page_num_from_url(self) -> Union[int, None]:
        """从url中获取页码"""
        if not self.num_param:
            return None

        if self.num_param.startswith('/'):
            r = search(f'{self.num_param}(\\d*)', self.url)
        else:
            r = search(f'{self.num_param}=(\\d*)', self.url)

        if r is None:
            return None

        num = int(r.group(1)) if r else None
        num = num // self.step + (1 - self.first_num)
        return num

    def _page_num_to_url_num(self, num: int) -> int:
        """把页码转换成url的数字                    \n
        :param num: 第几页
        :return: url中页码数字
        """
        return (num - 1 + self.first_num) * self.step

    def _get_pages_count_from_paths(self) -> Union[int, None]:
        """获取总页数"""
        if not self.paths.pages_count:
            return None

        total = self._get_value(self, self.paths.pages_count, '总页数', False)

        return int(total) if total else 1
