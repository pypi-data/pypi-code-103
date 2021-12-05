#!/usr/bin/env python

# Copyright 2020-2021 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import setuptools


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="pyflame",
    version="0.1.0",
    author="Daniel Harding",
    author_email="dharding@living180.net",
    description="Flamegraph generator for Python",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url="https://gitlab.com/living180/pyflame",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Django",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    packages=['pyflame'],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
)
