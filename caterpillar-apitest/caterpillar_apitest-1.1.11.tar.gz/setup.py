#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup

with open("README.md", "r", encoding="utf8") as f:
    long_description = f.read()

VERSION = "1.1.11"

setup(
    name="caterpillar_apitest",
    version=VERSION,
    description='基于pytest和数据驱动的接口自动化框架',
    long_description=long_description,
    author='redrose2100',
    author_email='hitredrose@163.com',
    maintainer='redrose2100',
    maintainer_email='hitredrose@163.com',
    license='MulanPSL2',
    packages=[],
    py_modules=["caterpillar_apitest"],
    install_requires=[
        "openpyxl",
        "caterpillar_log",
        "pytest"
    ],
    platforms=["all"],
    url='https://gitee.com/redrose2100/caterpillar_apitest',
    include_package_data=True,
    entry_points={
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ],
)
