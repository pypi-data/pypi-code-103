# -*- coding: utf-8 -*-

#  Author: Daniel Yang <daniel.yj.yang@gmail.com>
#
#  License: MIT

import setuptools

import treekit

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    required = fh.read().splitlines()

setuptools.setup(
    name="treekit",
    version=treekit.__version__,
    author="Daniel Yang",
    author_email="daniel.yj.yang@gmail.com",
    description="Library for Studying Tree Data Structure",
    license=treekit.__license__,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/daniel-yj-yang/treekit",
    packages=setuptools.find_packages(),
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    python_requires='>=3.8',
    include_package_data=True,
)
