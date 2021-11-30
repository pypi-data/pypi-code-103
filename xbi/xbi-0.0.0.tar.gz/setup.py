#!/usr/bin/env python

import setuptools
import xbi

with open('README.md', 'r') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='xbi',
    version=xbi.__version__,
    description='Simulation-based Inference with JAX',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords='parameter inference simulator jax',
    author='François Rozet',
    author_email='francois.rozet@outlook.com',
    url='https://github.com/francois-rozet/xbi',
    install_requires=required,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
