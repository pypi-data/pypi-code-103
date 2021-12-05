#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from setuptools import setup

is_test = 'pytest' in sys.argv or 'test' in sys.argv
setup(setup_requires=['pytest-runner>=2.0,<3dev'] if is_test else [])
