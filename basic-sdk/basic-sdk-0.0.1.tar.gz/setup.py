# -*- coding: utf-8 -*-
# @File    : setup.py
# @Time    : 2021/11/29 2:25 下午


from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().strip().splitlines()

setup(
    name="basic-sdk",  # 应用名
    version="0.0.1",  # 版本号
    url="https://github.com/Duanxinxin/basic_sdk",  # 代码地址
    author="dgz",
    description="General project functions",
    packages=['basic_sdk'],  # 包括在安装包内的 Python 包
    zip_safe=False,
    include_package_data=True,
    install_requires=required,
)
