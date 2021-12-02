#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 14:42:11 2019

@author: stefan
"""

import setuptools
from distutils.core import setup

with open("readme.md", "r") as fh:
    long_description = fh.read()
    
setup(name='Indago',
      version='0.1.10',
      description='Numerical optimization framework',
      author='sim.riteh.hr',
      author_email='stefan.ivic@riteh.hr',
      url='http://sim.riteh.hr/',
      py_modules=['indago',
                  'indago.optimizer',
                  'indago.pso',
                  'indago.fwa',
                  'indago.abca',
                  'indago.ssa',
                  'indago.direct_search',
                  'indago.de',
                  'indago.mmo',
                  'indago.benchmarks'],
      setup_requires=['wheel'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          ],
      python_requires='>=3.6',
)
