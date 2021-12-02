#!/usr/bin/env python
""" Setup for the pylint-print package. """

import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'pylint_print', '__version__.py'), 'r') as f:
    exec(f.read(), about) # pylint: disable=W0122

with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name=about['__title__'],
    description=about['__description__'],
    license=about['__license__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    install_requires=[
        'pylint',
    ],
    packages=['pylint_print'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
