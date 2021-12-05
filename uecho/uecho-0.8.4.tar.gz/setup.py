#!/usr/bin/env python
# Copyright (C) 2021 Satoshi Konno. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

with open("README.md", "r") as f:
    long_description=f.read()

setuptools.setup(
    name='uecho',
    version='0.8.4',
    description="uEcho for Python is a portable development framework for ECHONET Lite developers.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Satoshi Konno',
    author_email='skonno@cybergarage.org',
    url='https://github.com/cybergarage/uecho-py.git',
    install_requires=[
        'netifaces',
        'typing_extensions',	
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: Apache Software License',
    ],
)
