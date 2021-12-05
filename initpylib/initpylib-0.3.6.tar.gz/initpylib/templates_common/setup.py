#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from os.path import dirname, join as pjoin
from setuptools import setup
from tools import updatebadge

# Please Setting ----------------------------------------------------------
# If you wan't install compiled scripts by C++ etc

PROJECT_NAME = '_PLEASE_PYPROJECT_NAME_'

# -------------------------------------------------------------------------

thisdir = dirname(__file__)
__version__ = open(pjoin(thisdir, "VERSION"), "r").read().strip()

# OS Environment Infomation
is_test = 'pytest' in sys.argv or 'test' in sys.argv

# Readme badge link update.
updatebadge.readme(pjoin(thisdir, "README.md"), new_version=__version__)

setup(
    # to be package directory name.
    packages=[PROJECT_NAME],

    # Require pytest-runner only when running tests
    setup_requires=['pytest-runner>=2.0,<3dev'] if is_test else [],
)
# Other Setting to setup.cfg
