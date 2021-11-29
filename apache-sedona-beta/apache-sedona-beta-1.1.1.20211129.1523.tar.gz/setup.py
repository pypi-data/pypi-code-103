# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from setuptools import setup, find_packages
from os import path
from sedona import version
from datetime import datetime
import os
import subprocess

ATTACH_BRANCH_NAME = os.environ.get("ATTACH_BRANCH_NAME", None)
PROJECT_NAME = os.environ.get("PROJECT_NAME", "apache-sedona")

def get_version():
    directory = os.path.dirname(os.path.abspath(__file__))
    build_date_string = datetime.now().strftime("%Y%m%d.%H%M")
    try:
        branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD".split(),
            encoding="utf-8",
            cwd=directory,
        ).strip()
    except subprocess.CalledProcessError:
        branch = "unknown"

    tag = "dev"

    if branch.find("feature") == 0:
        tag = "-".join(branch[8:].split("-")[:2])
    elif branch.find("bugfix/") == 0:
        tag = branch.replace("/", "-")

    if ATTACH_BRANCH_NAME is None or branch == "master":
        version_number = f"{version}.{build_date_string}"
    else:
        version_number = f"{tag}.{version}.{build_date_string}"

    return version_number.replace("-", "_")


here = path.abspath(path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=PROJECT_NAME,
    version=get_version(),
    description='Apache Sedona is a cluster computing system for processing large-scale spatial data',
    url='https://sedona.apache.org',
    license="Apache License v2.0",
    author='Apache Sedona',
    author_email='dev@sedona.apache.org',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    install_requires=['attrs', "shapely"],
    extras_require={"spark": ['pyspark>=2.3.0']},
    project_urls={
        'Documentation': 'https://sedona.apache.org',
        'Source code': 'https://github.com/apache/incubator-sedona',
        'Bug Reports': 'https://issues.apache.org/jira/projects/SEDONA'
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License"
    ]
)

