#!/usr/bin/env python3
# argumentor - A simple, copylefted, lightweight library to work with command-line arguments in Python
# Copyright (C) 2021 Twann <twann@ctemplar.com>

# Import modules

import os.path
import sys
from argumentor.__init__ import __version__

# Check if setuptools is installed

try:
    from setuptools import setup
except ImportError:
    setup = None
    sys.exit("Error: setuptools is not installed\nTry to run python -m pip install setuptools --upgrade")

# Open README to define long description

with open(os.path.join(os.path.dirname(__file__), "README.md"), "rt") as readme:
    long_description = readme.read()

setup(
        name="argumentor",
        version=__version__,
        description="A library to work with command-line arguments",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://codeberg.org/twann/python-argumentor",
        author="Twann",
        author_email="twann@ctemplar.com",
        license="LGPLv3",
        packages=["argumentor"],
        classifiers=[
            "Environment :: Console",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Operating System :: OS Independent",
        ],
)
