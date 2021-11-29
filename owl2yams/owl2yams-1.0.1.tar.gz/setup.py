#!/usr/bin/env python
# coding: utf-8

import os.path as osp

from pathlib import Path
from setuptools import find_packages, setup

ROOT = Path(__file__).parent

here = osp.abspath(osp.dirname(__file__))
# Get the long description from the relevant file
with open(osp.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

distname = "owl2yams"
version = "1.0.1"
license = "LGPL"
description = "A tools to transforms owl into yams schema"
author = "Fabien Amarger"
author_email = "famarger@logilab.fr"
requires = {
    "cubicweb": ">=3.30, <3.33",
    "yams": ">=0.45.5",
    "rdflib": ">= 5.0.0, < 6.0.0",
    "rdflib-jsonld-without-2to3": ">= 0.7.0",  # to remove with rdflib 6
    "Jinja2": None,
    "black": None,
    "requests": None,
}
install_requires = ["{0} {1}".format(d, v or "").strip() for d, v in requires.items()]

setup(
    name=distname,
    version=version,
    license=license,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=author,
    url="https://forge.extranet.logilab.fr/cubicweb/owl2yams",
    author_email=author_email,
    packages=find_packages(exclude=["test"]),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={"console_scripts": ["owl2yams = owl2yams:main"]},
)
