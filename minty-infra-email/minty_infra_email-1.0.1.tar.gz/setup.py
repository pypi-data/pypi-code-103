#!/usr/bin/env python

# SPDX-FileCopyrightText: Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("requirements/base.txt") as f:
    requirements = f.read().splitlines()
    dependency_links = []
    for req in list(requirements):
        if req.startswith("git+"):
            requirements.remove(req)
            dependency_links.append(req)

with open("requirements/test.txt") as f:
    test_requirements = f.read().splitlines()

setup(
    author="Martijn van de Streek",
    author_email="martijn@mintlab.nl",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    description="Infrastructure class for sending email",
    setup_requires=["pytest-runner"],
    install_requires=requirements,
    dependency_links=dependency_links,
    license="EUPL license",
    long_description=readme,
    include_package_data=True,
    keywords="minty_infra_email",
    name="minty_infra_email",
    packages=find_packages(
        include=["minty_infra_email", "minty_infra_email.*"]
    ),
    package_data={"minty_infra_email": ["py.typed"]},
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.com/minty-python/minty-infra-email",
    version="1.0.1",
    zip_safe=False,
)
