from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.3'
DESCRIPTION = 'A basic visual package for helping Sloths team'
LONG_DESCRIPTION = 'A basic visual package for helping Sloths team'

# Setting up
setup(
    name="resultsbbb",
    version=VERSION,
    author="VS",
    author_email="email@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['plotly','pandas'],
    keywords=['python', 'Sloths', '360'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)