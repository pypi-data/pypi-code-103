"""
Setup to create the package
"""
from setuptools import setup, find_packages

import polidoro_terminal

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='polidoro-terminal',
    version=polidoro_terminal.VERSION,
    description='Terminal Terminal.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/heitorpolidoro/polidoro-terminal',
    author='Heitor Polidoro',
    license='unlicense',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    include_package_data=True
)
