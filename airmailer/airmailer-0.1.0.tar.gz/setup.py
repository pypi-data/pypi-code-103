#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'click>=8.0',
    'boto3>=1.17'
]

test_requirements = []

setup(
    author="Christopher Malek",
    author_email='cmalek@caltech.edu',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: Communications :: Email',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Use boto3 to send e-mails with AWS SES, with configuration set support",
    entry_points={
        'console_scripts': [
            'airmailer=airmailer.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['aws', 'email'],
    name='airmailer',
    packages=find_packages(include=['airmailer', 'airmailer.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/cmalek/airmailer',
    version='0.1.0',
    zip_safe=False,
)
