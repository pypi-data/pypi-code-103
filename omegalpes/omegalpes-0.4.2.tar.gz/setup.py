#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
OMEGAlpes installation script

:authors: B. DELINCHANT, S. HODENCQ, Y. MARECHAL, L. MORRIET,
          C. PAJOT, F. WURTZ
:license: Apache Software License 2.0
:version: 0.4.2
"""

from setuptools import setup, find_packages

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 4, 2)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------


setup(

    name='omegalpes',
    version=__version__,
    packages=["omegalpes",
              "omegalpes.energy",
              "omegalpes.energy.io",
              "omegalpes.energy.units",
              "omegalpes.energy.buildings",
              "omegalpes.general",
              "omegalpes.general.optimisation",
              "omegalpes.general.utils",
              "omegalpes.actor",
              "omegalpes.actor.operator_actors",
              "omegalpes.actor.project_developer_actors",
              "omegalpes.actor.regulator_actors",
              ],
    author="B. DELINCHANT, S. HODENCQ, Y. MARECHAL, L. MORRIET, "
           "C. PAJOT, V. REINBOLD, F. WURTZ",
    author_email='omegalpes-users@groupes.renater.fr',
    description="OMEGAlpes is a linear energy systems modelling library",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    install_requires=[
        "PuLP >= 2.1",
        "Matplotlib >= 2.2.2",
        "Numpy >= 1.14.2",
        "Pandas >= 0.25.0",
        "lpfics >= 0.0.1"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],

)
