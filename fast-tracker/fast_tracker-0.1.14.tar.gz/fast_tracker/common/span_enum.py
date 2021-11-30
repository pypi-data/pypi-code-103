# -*- coding: utf-8 -*-

from enum import Enum


class SpanType(Enum):
    """span类型"""
    Entry = 0 # 入口
    Exit = 1 # 外部调用
    Local = 2 # 本地调用

class SpanLayerAtrr(Enum):
    """
    span所属层的属性
    """
    Local = 0 # 本地
    DB = 1 # 数据库
    RPC = 2 # RPC框架
    HTTP = 3 # http调用
    MQ = 4 # 中间件
    CACHE = 5 # 缓存