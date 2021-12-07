#!/usr/bin/env python
"""Setup script for common """
import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

folder = os.path.dirname(os.path.realpath(__file__))
requirementPath = folder + "/requirements.txt"
install_requires = []
# The text of the requirements.txt
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

# This call to setup() does all the work
setup(
    name="tkcommon",
    version="1.0.4",
    description="tkcommon is a collection of small Python functions and classes for building scripts and internal tools.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/tekion/tkcommon",
    author="Vinoth Kumar",
    author_email="vinothkumarj@tekion.com",
    python_requires=">3.5.2",
    packages=["tkcommon"],
    package_dir={"tkcommon": "tkcommon/"},
    include_package_data=True,
    install_requires=install_requires,
)
