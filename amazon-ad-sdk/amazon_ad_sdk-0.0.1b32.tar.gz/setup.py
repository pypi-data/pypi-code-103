# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)
from setuptools import setup

setup(
    name='amazon_ad_sdk',
    version='0.0.1b32',
    packages=['amazon_ad',
              'amazon_ad.api',
              'amazon_ad.api.sb',
              'amazon_ad.api.sp',
              'amazon_ad.api.sd',
              'amazon_ad.api.dsp',
              'amazon_ad.client',
              'amazon_ad.core',
              'amazon_ad.core.utils',
              ],
    url='',
    license='',
    author='Ryan',
    author_email='931798845@qq.com',
    description='Amazon Advertising SDK',
    setup_requires=['wheel'],
    install_requires=[
        "arrow==0.12.1",
        "certifi==2018.10.15",
        "chardet==3.0.4",
        "idna==2.7",
        "ipython==7.2.0",
        "python-dateutil==2.7.5",
        "requests==2.20.1",
        "six==1.11.0",
        "urllib3==1.24.1",
        "wcwidth==0.1.9",
    ],
    python_requires='>=3.6',
)
