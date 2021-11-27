#!/usr/bin/env python

import re
import setuptools

version = ""
with open('xdj_datamap/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xdj-datamap",
    version=version,
    author="18580543261",
    author_email="595127207@qq.com",
    description="a datamap for django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",
    url="https://gitee.com/xdjango/xdj_datamap.git",
    install_requires=[
        "Django==3.2.3",
        "djangorestframework==3.12.4",
        "xdj-utils==0.0.4"
    ],
    packages=setuptools.find_packages(),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ),
    exclude_package_data={'': ["requirements.txt"]},
)
