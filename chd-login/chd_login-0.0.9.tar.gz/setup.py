#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chd_login",
    version="0.0.9",
    author="Oren Zhang",
    url="https://www.oren.ink/",
    author_email="oren_zhang@outlook.com",
    description="A Login Tool for CHD",
    packages=["chd_login"],
    install_requires=[
        "requests==2.20.1",
        "beautifulsoup4==4.9.3",
        "pycryptodome==3.10.1",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
