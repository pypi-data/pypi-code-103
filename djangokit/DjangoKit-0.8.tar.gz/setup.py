#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from setuptools import setup

# Dynamically calculate the version based on djangokit.VERSION.
version = __import__('djangokit').get_version()

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = [
        line.split('#', 1)[0].strip() for line in f.read().splitlines()
        if not line.strip().startswith('#')
    ]

with open('requirements-optional.txt') as f:
    optional_requirements = [
        line.split('#', 1)[0].strip() for line in f.read().splitlines()
        if not line.strip().startswith('#')
    ]


def option(package):
    for line in optional_requirements:
        if line.startswith(package):
            return line
    raise ValueError('Package %r not found.' % package)


setup(
    name="DjangoKit",
    version=version,
    author="Grigoriy Kramarenko",
    author_email="root@rosix.ru",
    description=("DjangoKit is a set of extensions for Django."),
    long_description=long_description,
    url="https://gitlab.com/djbaldey/djangokit/",
    license="BSD License",
    zip_safe=False,
    packages=['djangokit'],
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'markdown': [option('markdown')],
        'pygments': [option('pygments')],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.5",
)
