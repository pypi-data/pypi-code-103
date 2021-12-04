#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    readme = fh.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

test_requirements = []

setup(
    author="Alexander Angelo Ali",
    author_email='downtocrypto@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Tool for analysing sports betting and stock markets and other financial markets.",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='howitzer',
    name='howitzer',
    packages=find_packages(include=['howitzer', 'howitzer.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/aaaelite21/howitzer',
    version='0.3.0',
    zip_safe=False,
)
