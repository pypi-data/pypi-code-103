# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2020-11-17
# @email     : g1879@qq.com
# @File      : paths.py
from typing import Union


class Paths(object):
    """路径管理对象                        \n
    用于管理列表页面中关键元素的路径信息"""
    __attrs__ = ['rows', 'cols', 'page_count', 'next_btn', 'container']

    def __init__(self, path_type: str = None, paths_dict: dict = None):
        """初始化                                           \n
        :param path_type: 路径的类型， 'css' 或 'xpath'
        :param paths_dict: 包含路径信息的字典
        """
        self.type = path_type

        self._rows = None
        self._cols = {}
        self._next_btn = None
        self._pages_count = None
        self._more_btn = None
        self._container = None

        if paths_dict:
            self.from_dict(paths_dict)

    def __call__(self) -> dict:
        """调用时把路径信息以字典格式返回"""
        return self.as_dict()

    @property
    def type(self) -> str:
        """返回路径的类型，css或xpath"""
        if self._type is None:
            raise ValueError('路径类型未指定。')

        return self._type

    @type.setter
    def type(self, paths_type: str) -> None:
        """设置路径类型                        \n
        :param paths_type: 'css' 或 'xpath'
        :return: None
        """
        if paths_type not in ('css', 'xpath', None):
            raise ValueError("type参数只能为 'css' 或 'xpath'。")

        self._type = paths_type

    @property
    def rows(self) -> str:
        """返回行元素的路径"""
        return self._rows

    @rows.setter
    def rows(self, path: str) -> None:
        """设置行元素的路径         \n
        :param path: 行元素的路径
        :return: None
        """
        if not isinstance(path, str):
            raise TypeError('path参数只能是str。')

        self._rows = path

    @property
    def next_btn(self) -> str:
        """返回下一页按钮的路径"""
        return self._next_btn

    @next_btn.setter
    def next_btn(self, path: str) -> None:
        """设置下一页按钮的路径         \n
        :param path: 下一页按钮的路径
        :return: None
        """
        if not isinstance(path, str):
            raise TypeError('path参数只能是str。')

        self._next_btn = path

    @property
    def pages_count(self) -> Union[str, list, tuple]:
        """返回总页数元素的定位符列表"""
        return self._pages_count

    @pages_count.setter
    def pages_count(self, path_or_loc: Union[str, list, tuple]) -> None:
        """设置总页数元素的定位符                  \n
        :param path_or_loc: 总页数元素的定位符
        :return: None
        """
        if isinstance(path_or_loc, (list, tuple)) and not 0 < len(path_or_loc) < 4:
            raise ValueError('定位符格式不正确。应为str，或长度小于4的list或tuple。')

        self._pages_count = path_or_loc

    @property
    def container(self) -> str:
        """返回滚动列表页的容器路径"""
        return self._container

    @container.setter
    def container(self, path: str) -> None:
        """设置滚动列表页的容器路径    \n
        :param path: 容器的路径
        :return: None
        """
        if not isinstance(path, str):
            raise TypeError('path参数只能是str。')

        self._container = path

    @property
    def cols(self) -> dict:
        """返回保存的列路径"""
        return self._cols

    @cols.setter
    def cols(self, cols: Union[dict, list, tuple]) -> None:
        """批量设置列路径                               \n
        :param cols: dict、list或tuple格式保存的列信息
        :return: None
        """
        self.set_cols(cols)

    def get_col(self, col_name: str) -> str:
        """返回某列元素的路径                             \n
        :param col_name: 列名
        :return: 列的路径
        """
        return self._cols[col_name] if col_name in self._cols else None

    def set_cols(self, cols: Union[dict, list, tuple]) -> None:
        """批量设置列路径                               \n
        :param cols: dict、list或tuple格式保存的列信息
        :return: None
        """
        if isinstance(cols, dict):
            self._cols = cols

        elif isinstance(cols, (list, tuple)):
            # 一维数组，即 (key, path_str)
            if len(cols) == 2 and isinstance(cols[0], str) and isinstance(cols[1], str):
                self.set_col(cols[0], cols[1])

            # 二维数组，即 ((key, path_str), (key, path_str), ...)
            else:
                for i in cols:
                    if (not isinstance(i, (list, tuple)) or len(i) != 2
                            or not isinstance(i[0], str) or not isinstance(i[1], str)):
                        raise TypeError

                    self.set_col(i[0], i[1])

        else:
            raise TypeError('参数cols类型错误。')

    def set_col(self, col_name: str, path: str) -> None:
        """设置一列的路径                  \n
        :param col_name: 列名
        :param path: 列的路径
        :return: None
        """
        self._cols[col_name] = path

    def from_dict(self, paths_dict: dict):
        """从字典中读取并设置路径信息                  \n
        :param paths_dict: 以字典形式保存的列信息
        :return: 当前对象
        """
        self.type = get_paths_type_from_dict(paths_dict)

        for argument in paths_dict:
            if argument in self.__attrs__:
                if argument == 'cols':
                    self.set_cols(paths_dict['cols'])
                else:
                    setattr(self, argument, paths_dict[argument])

        return self

    def as_dict(self) -> dict:
        """把路径信息以字典格式返回"""
        return_dict = {key: getattr(self, key) for key in self.__attrs__}
        return_dict['type'] = self.type
        return return_dict


class Xpaths(Paths):
    def __init__(self, paths_dict: dict = None):
        """类型为xpath的路径类                      \n
        :param paths_dict: 以字典形式保存的路径信息
        """
        super().__init__(paths_dict=paths_dict)
        self._type = 'xpath'

    @property
    def type(self) -> str:
        """返回路径类型"""
        return super().type

    @type.setter
    def type(self, path_type: str) -> None:
        """重载父类属性，不允许改变该值                       \n
        :param path_type: 路径类型，'css'或'xpath'
        :return: None
        """
        pass


class CssPaths(Paths):
    def __init__(self, paths_dict: dict = None):
        """类型为css selector的路径类                      \n
        :param paths_dict: 以字典形式保存的路径信息
        """
        super().__init__(paths_dict=paths_dict)
        self._type = 'css'

    @property
    def type(self) -> str:
        """返回路径类型"""
        return super().type

    @type.setter
    def type(self, path_type: str) -> None:
        """重载父类属性，不允许改变该值                   \n
        :param path_type: 路径类型，'css'或'xpath'
        :return: None
        """
        pass


def get_paths_type_from_dict(paths_dict: dict) -> str:
    """从路径字典中获取路径类型                      \n
    :param paths_dict: 以字典形式保存的路径信息
    :return: 'xpath' 或 'css'
    """
    p_type = paths_dict.get('type', None)

    if not p_type:
        p_type = 'css'
        for i in paths_dict:
            if '/' in paths_dict[i]:
                p_type = 'xpath'
                break

    return p_type
