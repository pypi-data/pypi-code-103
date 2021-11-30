#!/usr/bin/env python3

# Libervia Desktop and Mobile Frontend
# Copyright (C) 2009-2021  Jérôme Poisson (goffi@goffi.org)
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
import textwrap

NAME = "libervia-desktop"
# NOTE: directory is still "cagou" for compatibility reason, should be changed for 0.9
DIR_NAME = "cagou"

install_requires = [
    'kivy >=2.0.0, <2.1.0',
    'kivy_garden.modernmenu',
    'pillow <8.3',
    'plyer <2.1',
    'libervia-backend >=0.8.0b1, <0.9',
]

with open(os.path.join(DIR_NAME, 'VERSION')) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith('D')


def cagou_dev_version():
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
    description="Desktop/Android frontend for Libervia XMPP client",
    long_description=textwrap.dedent("""\
        Libervia Desktop (Cagou) is a desktop/Android frontend for Libervia.
        It provides native graphical interface with a modern user interface,
        using touch screen abilitiy when available, and with split ability inspired from
        Blender
        """),
    author="Association « Salut à Toi »",
    author_email="contact@goffi.org",
    url="https://salut-a-toi.org",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications",
        "Framework :: Twisted",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Topic :: Internet :: XMPP",
        "Topic :: Communications :: Chat",
        "Intended Audience :: End Users/Desktop",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "libervia-desktop = cagou:run",
            "libervia-mobile = cagou:run",
            "cagou = cagou:run",
            ],
        },
    zip_safe=False,
    setup_requires=["setuptools_scm"] if is_dev_version else [],
    use_scm_version=cagou_dev_version if is_dev_version else False,
    install_requires=install_requires,
    package_data={"": ["*.kv"], "cagou": ["VERSION"]},
    python_requires=">=3.7",
)
