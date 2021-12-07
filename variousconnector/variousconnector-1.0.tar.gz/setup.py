# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:25:34 2021

@author: weiha
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="variousconnector", # 
    version="1.0",
    author="Weihao Li",
    author_email="weihao.li.tw@gmail.com",
    description="handy tools to connect the various data sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WeihaoLiTW/variousconnector",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires='>=3.6',
    install_requires=["sshtunnel", "sqlalchemy", "psycopg2", "pandas"],
)