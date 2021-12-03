# -*- coding: utf-8 -*-
import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="XunKuLogger",  # 包名
    version="0.0.2",  # 项目版本
    author="tianzhen2048",  # 作者名称
    author_email="1072575777@qq.com",  # 作者邮箱
    description="get a logger example",  # 项目概述
    long_description=long_description,  # 详细概述
    long_description_content_type="text/markdown",  # 标记类型，长描述标记类型
    url="http://www.xunku.org/",  # 项目位置，可以是git地址或者标注一下
    packages=setuptools.find_packages(),  # 直接用 setuptool 找到你项目所有相关的包列表
    # 附加说明，比如这里写的就是使用于 Python3 版本，使用的是 MIT 协议，独立于 OS
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
