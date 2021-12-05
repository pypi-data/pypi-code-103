#!/usr/bin/env python
from platform import python_branch
from setuptools import setup, find_packages

setup(
    name="Sithon",
    url="https://github.com/barrack-obama/Sithon",
    packages=find_packages(include=['sithon']),
    version="0.0.2",
    license="MIT",
    author="Simon G.",
    description="Sithon is a testing library for Python!",
    long_description=open('README.md', mode='r').read(),
    install_requires=["aiofiles"],
    python_requires=">=3.10"
)