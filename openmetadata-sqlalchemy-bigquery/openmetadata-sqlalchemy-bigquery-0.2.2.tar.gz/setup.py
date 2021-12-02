#!/usr/bin/env python
# Copyright (c) 2017 The sqlalchemy-bigquery Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import io
import itertools
import os
import re
from setuptools import setup

# Package metadata.

name = "openmetadata-sqlalchemy-bigquery"
description = "SQLAlchemy dialect for BigQuery by OpenMetadata"

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 5 - Production/Stable"

package_root = os.path.abspath(os.path.dirname(__file__))


def readme():
    with io.open("README.rst", "r", encoding="utf8") as f:
        return f.read()


extras = dict(
    geography=["GeoAlchemy2", "shapely"],
    alembic=["alembic"],
    tests=["packaging", "pytz"],
)
extras["all"] = set(itertools.chain.from_iterable(extras.values()))

setup(
    name=name,
    version="0.2.2",
    description=description,
    long_description=readme(),
    long_description_content_type="text/x-rst",
    author="The OpenMetadata Committers",
    author_email="googleapis-packages@google.com",
    packages=["sqlalchemy_bigquery"],
    url="https://github.com/open-metadata/OpenMetadata",
    keywords=["bigquery", "sqlalchemy"],
    classifiers=[
        release_status,
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
    ],
    platforms="Posix; MacOS X; Windows",
    install_requires=[
        "google-api-core>=1.30.0",  # Work-around bug in cloud core deps.
        # NOTE: Maintainers, please do not require google-auth>=2.x.x
        # Until this issue is closed
        # https://github.com/googleapis/google-cloud-python/issues/10566
        "google-auth>=1.25.0,<3.0.0dev",  # Work around pip wack.
        "google-cloud-bigquery>=2.25.2,<3.0.0dev",
        "sqlalchemy>=1.2.0,<1.5.0dev",
        "future",
    ],
    extras_require=extras,
    python_requires=">3.6",
    tests_require=["packaging", "pytz"],
    entry_points={
        "sqlalchemy.dialects": ["bigquery = sqlalchemy_bigquery:BigQueryDialect"]
    },
    # Document that this replaces pybigquery, however, this isn't
    # enforced by pip, because doing so would allow rogue packages to
    # obsolete legitimate ones.
    obsoletes=["pybigquery"],
)
