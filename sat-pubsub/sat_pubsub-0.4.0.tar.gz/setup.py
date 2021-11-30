#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SAT: an XMPP client
# Copyright (C) 2009-2016  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os

NAME = 'sat_pubsub'

install_requires = [
    'wokkel >= 0.7.1',
    'twisted >= 20.3.0',
    'psycopg2',
    'sat_tmp',
    'uuid',
]


with open(os.path.join(NAME, 'VERSION')) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith('D')


def sat_dev_version():
    """Use mercurial data to compute version"""
    def version_scheme(version):
        return VERSION.replace('D', '.dev0')

    def local_scheme(version):
        return "+{rev}.{distance}".format(
            rev=version.node[1:],
            distance=version.distance)

    return {'version_scheme': version_scheme,
            'local_scheme': local_scheme}


setup(
    name=NAME,
    version=VERSION,
    description="XMPP Publish-Subscribe Service Component, build for the need of "
                "the « Salut à Toi » project",
    author="Association « Salut à Toi »",
    author_email="goffi@goffi.org",
    url="https://salut-a-toi.org",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Twisted",
        "License :: OSI Approved :: GNU Affero General Public License v3 "
        "or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Communications :: Chat"
    ],
    packages=find_packages() + ["twisted.plugins"],
    data_files=[(os.path.join("share/doc", NAME),
                 ["CHANGELOG", "COPYING", "README"]),
                ],
    zip_safe=True,
    setup_requires=["setuptools_scm"] if is_dev_version else [],
    use_scm_version=sat_dev_version if is_dev_version else False,
    install_requires=install_requires,
    package_data={"sat_pubsub": ["VERSION"]},
    python_requires=">=3.6",
)
