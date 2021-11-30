#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Sistamapy - Simple statuses Mastodon for Python
Copyright (C) 2020 Vitor Guia

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()

setup(
    name='sepbit.sistamapy',
    version='1.0.0',
    long_description_content_type='text/markdown',
    description='Simple statuses Mastodon for Python',
    long_description=README,
    license='GPL-3.0-or-later',
    keywords='Statuses Mastodon Python',
    author='Vitor Guia',
    maintainer='Sepbit',
    maintainer_email='contato@sepbit.com',
    author_email='contato@vitor.guia.nom.br',
    url='https://gitlab.com/sepbit/sistamapy',
    packages=['sepbit.sistamapy'],
    python_requires='~=3.9',
    install_requires=['setuptools'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    test_suite='test',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    zip_safe=False,
)
