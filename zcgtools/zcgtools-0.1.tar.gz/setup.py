#!/python3
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import zcgtools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="zcgtools",
    version="0.1",
    author="Chenggang Zhao",
    author_email="zcgacbc@foxmail.com",
    description="Some tools writen by python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="",
    packages=find_packages(),
    install_requires=[
        ],
    classifiers=[
        "Topic :: Games/Entertainment ",
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Games/Entertainment :: Board Games',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
