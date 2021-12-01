import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "IATestMod",
    version = "0.0.3",
    author = "Craig Rixham",
    author_email = "crixham@paypal.com",
    description = ("Test module for pypi."),
    license = "BSD",
    keywords = "ia pypi demo",
    url = "http://packages.python.org/IATestMod",
    packages=['IATestMod'],
    #long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)