#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'sqlalchemy',
    'pyarrow'
]

setup_requirements = [
]

test_requirements = [
]

setup(
    name='sqlalchemy_dremio_flight',
    version='1.2.3',
    description="A SQLAlchemy dialect for Dremio via Flight interface.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Welly Tambunan",
    author_email='coach@wellytambunan.com',
    url='https://github.com/weltam/sqlalchemy_dremio',
    packages=find_packages(include=['sqlalchemy_dremio_flight']),
    entry_points={
        'sqlalchemy.dialects': [
            'dremio.flight = sqlalchemy_dremio_flight.flight:DremioDialect_flight',
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License",
    zip_safe=False,
    keywords='sqlalchemy_dremio_flight',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7'
    ]
)
