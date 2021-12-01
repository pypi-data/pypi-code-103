#! usr/bin/env python3
#  -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2020 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

"""
NoLOAD installation script
:version: 1.2.3
"""

from setuptools import setup, find_packages

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (1, 2, 3)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
# __docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------


setup(

    name='noload',
    version=__version__,
    packages=["noload",
              "noload.analyse",
              "noload.gui",
              "noload.optimization",
              "noload.tutorial",
              ],
    author="B. DELINCHANT, L. GERBAUD, F. WURTZ, L. AGOBERT",
    author_email='benoit.delinchant@G2ELab.grenoble-inp.fr',
    description="solving constrained optimization problem for the design of engineering systems",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    install_requires=[
        "Matplotlib >3.0",
        "Scipy >= 1.2",
        "Autograd >= 1.2"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],

)
