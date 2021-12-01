#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Paradox FINANCIAL GROUP LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from os.path import dirname, join

from setuptools import (
    find_packages,
    setup,
)

is_py3 = sys.version_info[0] == 3

with open(join(dirname(__file__), 'VERSION.txt'), 'rb') as f:
    version = f.read().decode('ascii').strip()

install_requires = ['requests>=2.25.1',
                    'urllib3>=1.25.8',
                    'numpy>=1.18.1',
                    'pandas>=1.1.3',
                    'websocket>=0.2.1',
                    'json5>=0.9.1',
                    'crypto==1.4.1',
                    'pymysql>=1.0.2'
                     ]

long_description = """
    Paradox Quantitative Data API is provided.
    The correspondingly market data and trading is supported in A market.
    see details in https://www.paradoxasset.com
"""

setup(
    name='paradoxapi',
    version=version,
    description='Paradox Quantitative Data API',
    classifiers=[],
    keywords='Paradox Stock Quant Data API',
    author='Paradox FINANCIAL GROUP LTD.',
    author_email='1013359736@qq.com',
    url='https://www.paradoxasset.com',
    license='Apache License 2.0',
    packages=find_packages(exclude=[]),
    package_data={'': ['*.*']},
    include_package_data=True,
    install_requires=install_requires,
    long_description=long_description
)
