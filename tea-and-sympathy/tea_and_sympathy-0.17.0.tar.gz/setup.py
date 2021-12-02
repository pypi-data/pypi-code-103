#!/usr/bin/env python
# encoding: UTF-8

import ast
from setuptools import setup
from setuptools import find_packages
import os.path

__doc__ = open(
    os.path.join(os.path.dirname(__file__), "README.rst"),
    "r"
).read()

try:
    # For setup.py install
    from tas import __version__ as version
except ImportError:
    # For pip installations
    version = str(ast.literal_eval(
        open(os.path.join(
            os.path.dirname(__file__),
            "tas",
            "__init__.py"),
            "r"
        ).readlines()[0].split("=")[-1].strip()
    ))


setup(
    name="tea_and_sympathy",
    version=version,
    description="An interactive screenplay.",
    author="D E Haynes",
    author_email="tundish@gigeconomy.org.uk",
    url="https://github.com/tundish/tea_and_sympathy",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3"
        " or later (AGPLv3+)"
    ],
    packages=find_packages(),
    package_data={
        "tas": [
            "css/*.css",
            "dlg/*.rst",
        ]
    },
    install_requires=[
        "aiohttp>=3.6.1",
        "balladeer>=0.19.0",
    ],
    extras_require={
        "dev": [
            "flake8>=3.7.0",
            "wheel>=0.33.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tas-web = tas.server:run",
        ],
    },
    zip_safe=True,
)
