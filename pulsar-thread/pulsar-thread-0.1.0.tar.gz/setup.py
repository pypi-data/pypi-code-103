# -*- coding: UTF-8 -*-
# @Time : 2021/11/28 下午11:17 
# @Author : 刘洪波
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pulsar-thread',
    version='0.1.0',
    packages=setuptools.find_packages(),
    url='https://gitee.com/maxbanana/pulsar',
    license='Apache',
    author='hongbo liu',
    author_email='782027465@qq.com',
    description='A connect pulsar message queue package, support multi-threaded production and consumption',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pulsar-client'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)