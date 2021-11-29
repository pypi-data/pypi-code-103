#!/usr/bin/env python
"""
suanpan sdk
"""

import os
import re

from setuptools import find_packages, setup

VERSION_PARRTERN = r"__version__ = \"v([\d\w\.]*)\""
VERSION_FILE = os.path.join("suanpan", "__init__.py")
VERSION = re.findall(VERSION_PARRTERN, open(VERSION_FILE, "r").read())[0]

the_lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = os.path.join(the_lib_folder, "requirements.txt")
INSTALL_REQUIRES = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        INSTALL_REQUIRES = f.read().splitlines()

README = "README.md"


def read_file(path):
    with open(path, "r") as f:
        return f.read()


packages = find_packages()

setup(
    name="python-suanpan-slim",
    version=VERSION,
    packages=packages,
    package_data={"": ["**/*.yaml"]},
    license="See License",
    author="yanqinghao",
    author_email="woshiyanqinghao@gmail.com",
    description="Suanpan SDK",
    long_description=read_file(README),
    long_description_content_type="text/markdown",
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
