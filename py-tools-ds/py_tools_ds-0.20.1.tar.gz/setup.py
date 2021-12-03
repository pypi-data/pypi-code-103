#!/usr/bin/env python
# -*- coding: utf-8 -*-

# py_tools_ds - A collection of geospatial data analysis tools that simplify standard
# operations when handling geospatial raster and vector data as well as projections.
#
# Copyright (C) 2016-2021
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
with open("py_tools_ds/version.py") as version_file:
    exec(version_file.read(), version)

requirements = [
    'gdal>=2.1.0',
    'numpy',
    'pandas',
    'pyproj>=2.5.0',
    'shapely',
    'spectral'
]
setup_requirements = ['setuptools']
test_requirements = requirements + ["gdal", "pytest", "pytest-cov", "pytest-reporter-html1", "shapely", "urlchecker"]

setup(
    name='py_tools_ds',
    version=version['__version__'],
    description="A collection of Python tools by Daniel Scheffler.",
    long_description=readme + '\n\n' + history,
    author="Daniel Scheffler",
    author_email='daniel.scheffler@gfz-potsdam.de',
    url='https://git.gfz-potsdam.de/danschef/py_tools_ds',
    packages=find_packages(exclude=['tests*']),  # searches for packages with an __init__.py and returns a list
    package_dir={'py_tools_ds': 'py_tools_ds'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache-2.0",
    zip_safe=False,
    keywords='py_tools_ds',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>3.6',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require={'rio_reproject': ["rasterio"]}
)
