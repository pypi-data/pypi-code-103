#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/26 14:20
# @Author  : Adyan
# @File    : setup.py


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zhanlan2",
    version="0.2.5",
    author="Adyan",
    author_email="228923910@qq.com",
    description="Special package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liujiang9/Utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
