#!/usr/bin/env python
# coding: UTF-8

from setuptools import setup, find_packages

setup(name='afwfcfg',
      version='2.0.1',
      description='afwf config module',
      py_modules=['afwfcfg.afwf_config', 'afwfcfg.afwf_evilTypeAction_config', 'afwfcfg.black_white_list',
                  'afwfcfg.afwf_log', 'afwfcfg.afwf_get_update_count', 'afwfcfg.version_config'],
      packages=find_packages(),
      include_package_data=False,
      install_requires=[],
      entry_points={
        'console_scripts': [
            'afwf_devbind = afwfcfg.devbind:main',
        ],
      }
      )
