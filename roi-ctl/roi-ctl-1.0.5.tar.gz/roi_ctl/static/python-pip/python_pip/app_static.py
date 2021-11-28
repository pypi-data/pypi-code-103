#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from os.path import dirname, abspath, join

"""
必须放到 MODULE_NAME 根路径
"""

def get_static():
    """
    获取静态资源路径
    """
    dirname_root = dirname(dirname(abspath(__file__)))
    return join(dirname_root, "static")

def get_package():
    """
    获取配置文件
    """
    dirname_root = dirname(dirname(abspath(__file__)))
    return join(dirname_root, "package.json")
