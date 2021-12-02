#!/usr/bin/env python
# coding=utf-8
import io
import os
from setuptools import setup, find_packages

setup(
    name='Appium-Python-Client-Monkey',
    version='1.0.0',
    description=(
        'Hot Patch For Appium-Pyhton-Client'
    ),
    author='CN-Robert-LIU',
    author_email='liujhon2019@163.com',
    license='Apache 2.0',
    packages=find_packages(include=['appium*']),
    long_description=io.open(os.path.join(os.path.dirname(
        '__file__'), 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    platforms=["all"],
    url='https://github.com/CN-Robert-LIU/appium-python-client-monkey',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=['Appium-Python-Client']
)
