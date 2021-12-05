from setuptools import setup, find_packages
import codecs
import os

with open('README.md') as f:
    long_description = f.read()

VERSION = '0.0.5'
DESCRIPTION = 'A Conversion package of Weights,Volumes,Currencys,Temperatures,Areas'
LONG_DESCRIPTION = 'A package which helps in conversion of  Weights,Volumes,Currencys,Temperatures,Areas'

# Setting up
setup(
    name="anything-conversion",
    version=VERSION,
    author="sairamdgr8",
    author_email="<sairamdgr8@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'convertor','conversion','anything', 'Area conversion', 'Weights conversion','Weight Conversion','Volume Conversion','Currency Conversion','Temperature Conversion','Area Conversion','Currency','Volume','Temperature','Weight', 'Area'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)