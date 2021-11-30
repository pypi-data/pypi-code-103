# encoding: utf-8
'''
@author: zyl
@file: setup.py
@time: 2021/11/10 18:06
@desc:
'''
from setuptools import setup, find_packages

setup(
    name='zyl_utils',
    version='0.0.7',
    description=(
        '自用utils'
    ),
    long_description=open('README.md').read(),
    author='张玉良',
    author_email='1137379695@qq.com',
    maintainer='张玉良',
    maintainer_email='1137379695@qq.com',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/ZYuliang/zyl-utils',
    install_requires=[
        "pandas",
        "transformers",
        "torch",
        "wandb",
        "loguru",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
