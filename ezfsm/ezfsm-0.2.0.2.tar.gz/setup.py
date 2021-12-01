#!/usr/bin/env python
# coding:utf-8

from setuptools import find_packages, setup

setup(
name='ezfsm',
version='0.2.0.2',
description='python/micropython easy fsm.',
author="Eagle'sBaby",
author_email='2229066748@qq.com',
maintainer="Eagle'sBaby",
maintainer_email='2229066748@qq.com',
packages=find_packages(),
platforms=["all"],
url='https://gitee.com/eagle-s_baby/fsm/tree/master',
license='Apache Licence 2.0',
classifiers=[
'Programming Language :: Python',
'Programming Language :: Python :: 3',
],
install_requires = ["graphviz"],
keywords = ['fsm', 'easy'],
python_requires='>=3', 
)