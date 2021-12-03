# -*- coding: utf-8 -*-
'''
@File  : setup.py
@Author: liubingfeng
@Date  : 2021/12/3 1:32 下午
@Desc  : 
'''

from setuptools import setup

dependencies = [
        'pyspark',
        'pandas',
    ]

setup(
    name="jkdaae",
    version="1.0",
    packages=["jkdaae"],
    install_requires=dependencies,
    url="https://github.com/users/Melting889/projects",
    license="MIT License",
    description="jike project",
    maintainer="jike data analysis group",
    maintainer_email="liubingfeng@clickwifi.net",
)

