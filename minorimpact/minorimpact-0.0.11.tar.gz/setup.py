#!/usr/bin/env python3

import minorimpact
from setuptools import find_packages, setup

with open('./README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='minorimpact',
    packages=find_packages(include=['minorimpact']),
    version=minorimpact.__version__,
    description='Personal utility library',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author='Patrick Gillan',
    author_email = 'pgillan@minorimpact.com',
    license='GPLv3',
    install_requires=['psutil'],
    setup_requires=[],
    tests_require=[],
    url = "https://github.com/minorimpact/python-minorimpact",
)
