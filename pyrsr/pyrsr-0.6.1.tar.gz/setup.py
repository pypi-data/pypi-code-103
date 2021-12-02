#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyrsr, A package providing relative spectral response functions for remote sensing instruments.
#
# Copyright (C) 2019-2021
# - Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
# - Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences Potsdam,
#   Germany (https://www.gfz-potsdam.de/)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("pyrsr/version.py") as version_file:
    exec(version_file.read(), version)

requirements = ['numpy', 'pandas', 'matplotlib', 'scipy']

setup_requirements = ['setuptools-git']  # needed for package_data version controlled by GIT

test_requirements = ['coverage', 'nose', 'nose-htmloutput', 'rednose', 'urlchecker']


setup(
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A package providing relative spectral response functions for remote sensing instruments.",
    install_requires=requirements,
    license="Apache-2.0",
    long_description=readme + '\n\n' + history,
    package_dir={'pyrsr': 'pyrsr'},
    include_package_data=True,
    # NOTE: if the 'package_data' files are not under CVS or Subversion version control, we need setuptools-git here,
    #       otherwise they are not included in the PyPi upload content
    package_data={"pyrsr": ["data/**/**/*"]},
    keywords=['pyrsr', 'relative spectral response', 'remote sensing', 'sensors'],
    name='pyrsr',
    packages=find_packages(exclude=['tests*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://git.gfz-potsdam.de/geomultisens/pyrsr',
    version=version['__version__'],
    zip_safe=False,
)
