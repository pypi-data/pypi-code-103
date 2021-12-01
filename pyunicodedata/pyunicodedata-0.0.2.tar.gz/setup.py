#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : setup.py
@Time    : 2021/11/30 23:37
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2021 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyunicodedata",
    version="0.0.2",
    author="ZENKR",
    author_email="zenkr@qq.com",
    description="A package including Unicode UCD.zip and Unihan.zip",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zenkr/pyunicodedata",
    project_urls={
        "Document": "https://github.com/zenkr/pyunicodedata",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
