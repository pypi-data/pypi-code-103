import setuptools

import io
import os
import re

with io.open('pydrivelist/version.py', 'rt', encoding='utf-8') as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydrivelist",
    version=version,
    author="Nelson Brown, FAA Human Factors, ANG-E25",
    author_email="nelson.brown@faa.gov",
    description="Python Package for Listing Paths to Drive Identifiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://atmseminar.org/",
    entry_points={
        'console_scripts': ['pydrivelist=pydrivelist.main:main'],
    },
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        ],
    install_requires=['PyDrive2 >= 1.10.0'],
    python_requires='>=3.6',
)
