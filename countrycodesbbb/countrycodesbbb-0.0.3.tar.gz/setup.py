from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'A basic package for helping Sloths team with country codes'
LONG_DESCRIPTION = 'A basic package for helping Sloths team with country codes'

# Setting up
setup(
    name="countrycodesbbb",
    version=VERSION,
    author="VS",
    author_email="email.com@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'Sloths', '360','country codes'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)



