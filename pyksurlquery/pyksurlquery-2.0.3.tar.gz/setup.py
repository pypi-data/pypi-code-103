#!/usr/bin/env python
# coding: UTF-8

from setuptools import setup, find_packages

setup(
      name='pyksurlquery',
      version='2.0.3',
      description='url query module',
      py_modules=['pyksurlquery.mmatch', 'pyksurlquery.urltype_def'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=['chardet==3.0.4', 'requests==2.11.1', "urllib3==1.26.6"],
      )
