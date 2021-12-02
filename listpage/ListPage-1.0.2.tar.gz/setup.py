#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="ListPage",
    version="1.0.2",
    author="g1879",
    author_email="g1879@qq.com",
    description="Page classes dedicated to crawling or manipulating list web pages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    keywords="Page classes",
    url="https://gitee.com/g1879/ListPage",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "DrissionPage", "DataRecorder"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.6'
)
