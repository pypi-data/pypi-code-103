#!/usr/bin/env python3

# Libervia templates: collection of templates
# Copyright (C) 2017-2021  Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2017  Xavier Maillard (xavier@maillard.im)

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

import os
from setuptools import setup, find_packages

NAME = "libervia-templates"
# NOTE: directory is still "sat_templates" for compatibility reason,
#   should be changed for 0.9
DIR_NAME = "sat_templates"


with open(os.path.join(DIR_NAME, "VERSION")) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith("D")


def sat_templates_dev_version():
    """Use mercurial data to compute version"""
    def version_scheme(version):
        return VERSION.replace("D", ".dev0")

    def local_scheme(version):
        return "+{rev}.{distance}".format(
            rev=version.node[1:],
            distance=version.distance)

    return {"version_scheme": version_scheme,
            "local_scheme": local_scheme}


setup_info = dict(
    name=NAME,
    version=VERSION,
    description="Templates for Libervia XMPP client",
    long_description="Libervia Template is a common module which can be used by any SàT "
                     "frontend to generate documents (mostly HTML but not only).",
    author="Association « Salut à Toi »",
    author_email="contact@salut-a-toi.org",
    url="https://salut-a-toi.org",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later "
        "(AGPLv3+)",
    ],
    install_requires=[],
    setup_requires=["setuptools_scm"] if is_dev_version else [],
    use_scm_version=sat_templates_dev_version if is_dev_version else False,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)

setup(**setup_info)
