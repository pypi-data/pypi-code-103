#!/usr/bin/env python3
# encoding: UTF-8

from setuptools import setup, find_packages
import pathlib

VERSION = '0.9.1'
DESCRIPTION = 'Simulates and visualises transport of loadunits in a warehouse environment.'

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.rst').read_text(encoding='utf-8')

setup(
    name='ftsim',
    version=VERSION,
    author="Gerhard Sachs",
    author_email="<g.w.sachs@gmx.de>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url = "https://github.com/gerpark/ftsim",
    license='MIT',
    keywords = ['tkinter', 'sqlite', 'threading', 'game'],
    packages=find_packages(include=['ftsim', 'ftsim.*']),
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.db', '*.xml', '*.png'],
        },
    entry_points={
        #                :  script=dir.file:function
        'console_scripts': ['ftsim=ftsim.ftmain9:ftmain'],
        },
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ]
    )
