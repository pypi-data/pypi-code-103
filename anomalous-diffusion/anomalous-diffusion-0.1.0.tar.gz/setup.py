#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time : 2021/12/4 06:11
from setuptools import setup
from setuptools import find_packages


with open("README.md") as f:
   LONG_DESCRIPTION = f.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Physics",
]

VERSION = '0.1.0'

setup(
    url="https://github.com/tangxiangong/ClassTop/",
    name='anomalous-diffusion',  # package name
    version=VERSION,  # package version
    description='Anomalous diffusion simulation',  # package description
    long_description= LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    keywords=["anomalous diffusion", "stochastic process"],
    author="tang xiangong",
    author_email="tangxg16@gmail.com",
    python_requires=">=3.6",
    install_requires=[
        "numpy >= 1.17",
        "scipy >= 1.3",
        "stochastic >= 0.4",
        "matplotlib >= 3.1",
    ],
    extras_require={
        "dotenv": ["python-dotenv"],
        "dev": [
            "pytest",
            "coverage",
            "tox",
            "sphinx",
            "pallets-sphinx-themes",
            "sphinxcontrib-log-cabinet",
            "sphinx-issues",
        ],
        "docs": [
            "sphinx",
            "pallets-sphinx-themes",
            "sphinxcontrib-log-cabinet",
            "sphinx-issues",
        ],
    },
    packages=find_packages(),
    zip_safe=False,
)