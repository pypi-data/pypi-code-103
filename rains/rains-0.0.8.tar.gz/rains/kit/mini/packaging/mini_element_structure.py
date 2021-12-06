# !/usr/bin/env python
# coding:utf-8

"""
Copyright (c) 2021. quinn.7@foxmail.com All rights reserved.
Based on the Apache License 2.0 open source protocol.

作者 cat7
邮箱 quinn.7@foxmail.com

"""


__all__ = ['MiniElementStructure']


class MiniElementStructure(object):
    """
    [ 小程序元素结构体 ]
    * 无

    """

    page: str
    """ 页面名称 """

    name: str
    """ 组件名称 """

    selector: str
    """ 元素选择器字符串 """

    inner_text: str
    """ 控件内的文字 """

    text_contains: str
    """ 控件内的模糊文字 """

    value: str
    """ 控件的 value 值 """

    def __init__(self,
                 page: str,
                 name: str,
                 selector: str,
                 inner_text: str = None,
                 text_contains: str = None,
                 value: str = None):
        """
        [ 初始化 ]
        * 通过 selector 选择器对元素进行描述，返回包含该元素信息的元素对象。

        [ 必要参数 ]
        * page (str) : 页面名称
        * name (str) : 组件名称
        * selector (str) : css选择器或以/或//开头的xpath

        [ selector 选择器 ]
        * ID选择器: #the-id
        * class选择器（可以连续指定多个）: .a-class.another-class
        * 标签选择器: view
        * 子元素选择器: .the-parent > .the-child
        * 后代选择器: .the-ancestor .the-descendant
        * 跨自定义组件的后代选择器: custom-element1>>>.custom-element2>>>.the-descendant
        * 多选择器的并集：#a-node, .some-other-nodes
        * xpath：可以在真机调试的 wxml pannel 选择节点->右键->copy->copy full xpath获取，暂不支持[text()='xxx']这类xpath条件

        """

        # 获取元素参数
        self.page = page
        self.name = name
        self.selector = selector
        self.inner_text = inner_text
        self.text_contains = text_contains
        self.value = value
