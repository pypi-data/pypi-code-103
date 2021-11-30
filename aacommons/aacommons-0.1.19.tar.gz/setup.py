# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='aacommons',
    version='0.1.19',
    description='aacommons',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Thomas Bastian, Jeffrey Goff, Albert Pang',
    url='',
    test_suite="tests",
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "hiredis",
        "jstyleson",
        "munch",
        "PyYAML",
        "redis",
        "requests",
        "urllib3"
    ]
)
