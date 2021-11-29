#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='Xtssort',
    version='0.0.2',
    description=(
        'sort'
    ),
    long_description=open('README.rst').read(),
    author='xiongtianshuo',
    author_email='seoul1k@163.com',
    maintainer='xiontianshuo',
    maintainer_email='seoul1k@163.com',
    license='BSD License',
    packages=find_packages('example.py'),
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
)
