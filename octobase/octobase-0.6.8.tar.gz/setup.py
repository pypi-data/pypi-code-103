#!/usr/bin/env python3
#
# command to build:
#
#     ./setup.py sdist
#
# command to upload:
#
#     twine upload dist/octobase-0.6.7.tar.gz
#

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name            = 'octobase',
    version         = '0.6.8',
    author          = 'Octoboxy',
    author_email    = 'office@octoboxy.com',
    description     = 'The First Building Block For Any Python Project',
    url             = 'https://bitbucket.org/octoboxy/octobase/',
    python_requires = '>=3.6',
    classifiers     = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
    ],
    packages        = setuptools.find_packages(),
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
)
