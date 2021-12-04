import os
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README')) as f:
    long_description = f.read()


setup(
    name         = 'ingredient_parser',

    version      = '1.0.2',
    packages     = find_packages(exclude=['bin','lib','include','contrib', 'docs', 'tests']),


    description      = 'Parsing English and Swedish language ingredients into name and measure of the ingredient.',
    long_description = long_description,

    author       = 'Mark Anderson',
    author_email = 'mark+pypy@m3b.net',

    license      = 'MIT License',

    keywords     = 'recipes ingredient parsing food',

    url          = 'https://bitbucket.org/phoodster/ingredient-parser',

    platforms    = ['OS Independent'],

    classifiers  = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],)
