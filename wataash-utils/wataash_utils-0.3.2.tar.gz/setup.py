# SPDX-License-Identifier: Apache-2.0

# https://click.palletsprojects.com/en/7.x/setuptools/

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='wataash_utils',
    version='0.3.2',
    url='https://github.com/wataash/wataash_utils_py',
    author='Wataru Ashihara',
    author_email='wataash@wataash.com',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    license='Apache-2.0',
    description='wataash\'s personal utilities',
    long_description=long_description,
    keywords='wataash_utils',
    install_requires=[
        'click>=8.0.1',
        'logzero>=1.6.3',
        'wcwidth>=0.2.5',
    ],
    packages=find_packages(),
)
