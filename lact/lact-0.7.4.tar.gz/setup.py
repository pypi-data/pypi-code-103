#!python
from __future__ import print_function
from setuptools import setup, find_packages
import lact

with open("lact/README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="lact",
    version=lact.__version__,
    author="Linty Liu Tingli",
    author_email="liu.tingli@outlook.com",
    description="free automation testing tool powered by python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU GPLv3",
    url="",
    packages=find_packages(),
    install_requires=[
        "pytest>= 5.2.2",
        "requests>= 2.21.0",
        "pymysql>= 0.9.3",
        "pyyaml>= 5.1.2",
        "allure-pytest>= 2.6.3",
        "pytest-html>= 1.20.0",
        "pytest-rerunfailures>= 7.0",
        "pycryptodome>=3.9.1",
        "lxml>=4.4.0",
        "beautifulsoup4>=4.8.1",
        "coverage>= 4.5.1",
        "pillow>=6.2.1",
        "pytesseract>=0.3.1",
        "urllib3>=1.24.2",
        "selenium>= 3.141.0",
        "loguru>=0.5.1",
        "jsonpath>=0.82",
        ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
