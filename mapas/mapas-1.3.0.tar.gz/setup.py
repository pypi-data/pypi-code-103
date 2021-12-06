#!/usr/bin/env python3
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

with open(path.join(here, 'mapas', 'version.txt')) as f:
    version = f.read().strip()

setup(
    name='mapas',
    description='Create static maps from different layers',
    long_description=long_description,
    url='https://gitlab.com/categulario/mapas-py',

    version=version,

    author='Abraham Toriz Cruz',
    author_email='categulario@gmail.com',
    license='GPLv3',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    keywords='map, mapa, static map',

    packages=find_packages(),

    package_data={
        'mapas': ['version.txt'],
    },

    entry_points={
        'console_scripts': [],
    },

    install_requires=[
        'requests',
        'Pillow>=7.0,<8.0',
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest',
        'pytest-mock',
    ],
)
