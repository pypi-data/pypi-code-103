#!/usr/bin/env python
# -*- coding: utf-8 -*-

# geoarray, A fast Python interface for image geodata - either on disk or in memory.
#
# Copyright (C) 2017-2021
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

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("geoarray/version.py") as version_file:
    exec(version_file.read(), version)

req = [
    'cartopy',
    'dill',
    'gdal>=2.1.0',
    'matplotlib',
    'numpy',
    'pandas',
    'pyepsg',  # optional dependency of cartopy, needed by geoarray
    'py_tools_ds>=0.19.0',
    'scikit-image',
    'shapely'
    ]

req_interactive_plotting = [
    'folium',
    'geojson',
    'holoviews'
]

req_setup = ['setuptools-git']

req_test = req + ["coverage", "nose", "nose2", "nose-htmloutput", "rednose", "urlchecker", "parameterized"]

req_doc = ['sphinx-argparse', 'sphinx_rtd_theme']

req_lint = ['flake8', 'pycodestyle', 'pydocstyle']

req_dev = req_setup + req_test + req_doc + req_lint

setup(
    name='geoarray',
    version=version['__version__'],
    description="Fast Python interface for geodata - either on disk or in memory.",
    long_description=readme,
    author="Daniel Scheffler",
    author_email='danschef@gfz-potsdam.de',
    url='https://git.gfz-potsdam.de/danschef/geoarray',
    packages=find_packages(exclude=['tests*']),  # searches for packages with an __init__.py and returns a list
    package_dir={'geoarray': 'geoarray'},
    include_package_data=True,
    install_requires=req,
    license="Apache-2.0",
    zip_safe=False,
    keywords=['geoarray', 'geoprocessing', 'gdal', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>3.6',
    test_suite='tests',
    tests_require=req_test,
    setup_requires=req_setup,
    extras_require={
        "interactive_plotting": req_interactive_plotting,
        "doc": req_doc,
        "test": req_test,
        "lint": req_lint,
        "dev": req_dev
    }
)
