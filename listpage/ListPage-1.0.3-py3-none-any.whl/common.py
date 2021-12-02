# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2020-11-17
# @email     : g1879@qq.com
# @File      : common.py
from typing import Tuple, Union


def format_loc(loc: Union[str, list, tuple]) -> Tuple[str, str, str]:
    """将传入的定位符规范化                                          \n
    :param loc: 简写的定位符：(xpath或css路径, [属性名, 正则表达式])
    :return: 规范的定位符
    """
    re_str = '(.*)'

    if isinstance(loc, str):
        xpath_str, attr_str = loc, 'text'

    elif isinstance(loc, (list, tuple)):
        length = len(loc)

        if length == 1:
            xpath_str, attr_str = loc[0], 'text'
        elif length == 2:
            xpath_str, attr_str = loc
        elif length == 3:
            xpath_str, attr_str, re_str = loc
        else:
            raise ValueError('定位符位数不正确，应为(xpath或css路径, [属性名, 正则语句])。')

    else:
        raise ValueError('只能传入str、list或tuple。')

    return xpath_str, attr_str, re_str
