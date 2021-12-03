# -*- coding: utf-8 -*-
'''
@File  : func.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  :
'''

from setuptools import setup,find_packages

dependencies = [
        'pyspark',
        'pandas',
    ]

setup(
    name="jklwcs",
    version="1.1.1",
    packages=find_packages(),
    install_requires=dependencies,
    url="https://github.com/users/Melting889/projects",
    license="MIT License",
    description="jike project",
    maintainer="Jike Data Analysis Modeling Group",
    maintainer_email="liubingfeng@clickwifi.net",
)

