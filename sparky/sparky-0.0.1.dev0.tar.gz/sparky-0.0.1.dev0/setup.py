#! /usr/bin/env python
from setuptools import find_packages

DESCRIPTION = "Helpers for frequent work with pyspark"
LONG_DESCRIPTION = """\
Sparky provides helper functions, classes, and methods that are useful for
common routines done with pyspark.

Sparky provides:
- Functions for performing frequent data summarization and transformation tasks
  in pyspark data pipelines
- Classes and methods for common machine learning workflows using MLlib
- Classes and methods for pyspark system configuration
  
All Sparky wheels distributed on PyPI are BSD 3-clause licensed.
"""

DISTNAME = "sparky"
MAINTAINER = "Charles Kelley"
MAINTAINER_EMAIL = "cksisu@gmail.com"
URL = "https://sparky.readthedocs.io.org"
LICENSE = "BSD (3-clause)"
DOWNLOAD_URL = "https://github.com/cksisu/sparky"
VERSION = "0.0.1.dev0"
PYTHON_REQUIRES = ">=3.7"

CLASSIFIERS = [
    "Development Status :: 1 - Planning",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9"]


if __name__ == "__main__":

    from setuptools import setup

    import sys
    if sys.version_info[:2] < (3, 7):
        raise RuntimeError("preso requires python >= {0}.".format(PYTHON_REQUIRES))

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        python_requires=PYTHON_REQUIRES,
        package_dir={"": "sparky"},
        packages=find_packages(where="sparky"),
        classifiers=CLASSIFIERS)

