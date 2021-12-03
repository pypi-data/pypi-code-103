#!/usr/bin/env python3

import setuptools
from distutils.core import setup

def read_version(fpath):
    with open(fpath) as f:
        for line in f.readlines():
            if line.startswith('__version__'):
                return line.strip().split()[-1][1:-1]
    raise Exception('Version not found')


VERSION = read_version('./treedecomp.py')


with open("README.md", "r") as fh:
    long_description = fh.read()


CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
Topic :: Scientific/Engineering
Operating System :: OS Independent
"""

setup(name='treedecomp',
      version=VERSION,
      description='Python Class for Tree Decomposition',
      long_description=long_description,
      long_description_content_type="text/markdown",
      maintainer='Sebastian Will',
      maintainer_email='sebastian.will@polytechnique.edu',
      author='Sebastian Will',
      author_email='sebastian.will@polytechnique.edu',
      url='https://gitlab.inria.fr/amibio/treedecomp',
      classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
      py_modules=['treedecomp'],
      python_requires='>=3.6'
      )
