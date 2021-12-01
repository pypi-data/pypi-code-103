#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='autoCompile-hardhat',
    version='0.0.3',
    author='th35tr0n9',
    author_email='th35tr0n9@gmail.com',
    url='https://baidu.com',
    description=u'A script for hardhat auto compile.',
    packages=['autoCompileHardhat'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'autoC=autoCompileHardhat:main',
        ]
    }
)