# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 09:23:52 2020

@author: 35732
"""

from __future__ import print_function
from setuptools import setup, find_packages
import sys
import setuptools
 
setup(
      name="SuperalloyDigger",
      version="0.1.5",
      author="Weiren_Wang",
      author_email="357329191@qq.com",
      description="Automatic extraction of chemical compositions and properties from the scientific literature of superalloy, covering specific chemical composition, density, solvus temperature, solidus temperature, and liquidus temperature.",
      long_description=open("README.md",encoding="utf-8").read(),
      keywords='text-mining, superalloy, informatics, nlp, txt, science, scientific',
      license="MIT",
      url="https://github.com/Weiren1996/superalloydigger",
      packages=setuptools.find_packages(),
      long_description_content_type="text/markdown",
      classifiers=[
              "Environment :: Web Environment",
              "Intended Audience :: Science/Research",
              "Operating System :: Microsoft :: Windows",
              "Programming Language :: Python :: 3",
              "Topic :: Internet",
              "Topic :: Scientific/Engineering",
              "Topic :: Text Processing",
              ],
      python_requires='>=3.6'
)