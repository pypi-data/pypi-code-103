# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['WebElementStructure']


class WebElementStructure(object):
    """
    [ WEB元素结构体 ]
    * 无

    """

    page: str
    """ 页面名称 """

    name: str
    """ 组件名称 """

    by_key: str
    """ 元素定位策略 """

    by_value: str = ''
    """ 元素定位策略对应的值 """

    anchor_by_key: str
    """ 锚点元素定位策略 """

    anchor_by_value: str
    """ 锚点元素定位策略 """

    anchor_location_id: int
    """ 锚点元素定位ID """

    def __init__(self,
                 page: str,
                 name: str,
                 by_key: str,
                 by_value: str,
                 anchor_by_key: str = None,
                 anchor_by_value: str = None,
                 anchor_location_id: int = None):
        """
        [ 初始化 ]
        * 构建组件时，需要传递组件于页面上的定位方式(by_key)与相应的值(by_value)。
        * 当传递了非必须的锚点元素时，表示将在该锚点节点中定位元素。
        * 如果传递锚点元素(anchor)，则必须同时传递 anchor_by_key、anchor_by_value、anchor_location_id。

        [ 必要参数 ]
        * page (str) : 页面名称
        * name (str) : 组件名称
        * by_key (str) : 元素定位策略
        * by_value (str) : 元素定位策略对应的值

        [ 可选参数 ]
        * anchor_by_key (str) : 锚点元素定位策略
        * anchor_by_value (str) : 锚点元素定位策略
        * anchor_location_id (str) : 锚点元素定位ID

        [ 返回内容 ]
        * 无

        """

        # 获取元素参数
        self.page = page
        self.name = name
        self.by_key = by_key
        self.by_value = by_value
        self.anchor_by_key = anchor_by_key
        self.anchor_by_value = anchor_by_value
        self.anchor_location_id = anchor_location_id
