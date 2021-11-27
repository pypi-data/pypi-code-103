"""setup file for places geocoding package"""
from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent

VERSION = '0.1.7'
DESCRIPTION = 'Package for Places Geocoding API service'

# Setting up
setup(
    name="places_geocode",
    version=VERSION,
    author="Martin Mashalov",
    author_email="hello@places.place",
    description=DESCRIPTION,
    long_description=open('/Users/martinmashalov/Documents/places_geocoding_package/README.md').read(),
    long_description_content_type="text/markdown",
    packages=['places_geocode'],
    license="MIT",
    install_requires=['pymongo', 'numpy', 'pandas', 'sklearn', 'dependency_injector', 'pydantic', 'fastapi', 'cython',
                      'state_machine'],
    keywords=['python',
              'geocoding',
              'forward geocoding',
              'reverse geocoding',
              'radius loading',
              'loading radius',
              'autocomplete',
              'places of interest',
              'POI'
              ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: Free for non-commercial use",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)