from setuptools import setup
import os

# specify requirements of your package here
REQUIREMENTS = ['argparse']

# some more details
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Games/Entertainment :: Role-Playing',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
]

# calling the setup function 
setup (
    name='vntools',
    version='0.1.7',
    description='Parser for writing Godot visual novels in a text editor.',
    long_description=
    """
=======
vntools
=======

A simple compiler (really parser) for Visual Novels
Written for Care Jam 2021

The code is Python 3, I have not tried other versions presently.

Installation
------------

Fast install:

::

    pip install vntools

For a manual install get this package:

::

    wget https://github.com/LilithDaly/Visual-Novel-Tools/archive/refs/heads/main.zip
    unzip main.zip
    rm main.zip

Install the package:

::

    py setup.py install

""",
    url='https://github.com/LilithDaly/Visual-Novel-Tools',
    author='Lil',
    author_email='contact@lilithdaly.com',
    license='MIT',
    packages=[],
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    keywords='games writing compiler'
)