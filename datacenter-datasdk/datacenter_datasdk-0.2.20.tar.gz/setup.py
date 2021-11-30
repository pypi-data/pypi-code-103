# -*-coding:utf-8 -*-

"""
1. python setup.py sdist bdist_wheel
2. twine upload dist/*
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="datacenter_datasdk",
    version="0.2.20",
    author="Wang Sheng",
    author_email="jayed008@163.com",
    description="datacenter_datasdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'pandas>=0.25.3',
        'numpy>=1.18.4',
        'python-dateutil',
        'psycopg2-binary~=2.8.6',
        'requests==2.26.0',
        'SQLAlchemy',
        'ahttp==1.1.1',
        'nest-asyncio==1.5.1'
    ],
    zip_safe=True,
)
