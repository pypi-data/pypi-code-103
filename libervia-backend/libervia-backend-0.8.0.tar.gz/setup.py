#!/usr/bin/env python3

# Libervia: an XMPP client
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

NAME = "libervia-backend"
# NOTE: directory is still "sat" for compatibility reason, should be changed for 0.9
DIR_NAME = "sat"

install_requires = [
    'babel < 3',
    'dbus-python < 1.3',
    'html2text < 2020.2',
    'jinja2>=2.10.3',
    'langid < 2',
    'lxml >= 3.1.0',
    'markdown >= 3.0',
    'miniupnpc < 2.1',
    'mutagen < 2',
    'netifaces < 0.12',
    'pillow >= 6.0.0',
    'progressbar2 < 3.54',
    'cryptography < 3.5',
    'pygments < 3',
    'pygobject < 3.40.1',
    'pyopenssl < 21.0.0',
    'python-dateutil >= 2.8.1, < 3',
    'python-potr < 1.1',
    'pyxdg < 0.30',
    'sat_tmp >= 0.8.0b1, < 0.9',
    'shortuuid < 1.1',
    'twisted[tls] >= 20.3.0, < 21.3.0',
    'treq < 22.0.0',
    'urwid >= 1.2.0, < 3',
    'urwid-satext >= 0.8.0b1, < 0.9',
    'wokkel >= 18.0.0, < 19.0.0',
    'omemo >= 0.11.0, < 0.13.0',
    'omemo-backend-signal < 0.3',
    'pyyaml < 5.5.0',
]

extras_require = {
    "SVG": ["CairoSVG"],
}

DBUS_DIR = 'dbus-1/services'
DBUS_FILE = 'misc/org.libervia.Libervia.service'
with open(os.path.join(DIR_NAME, 'VERSION')) as f:
    VERSION = f.read().strip()
is_dev_version = VERSION.endswith('D')
if is_dev_version:
    install_requires.append("setuptools_scm")


def sat_dev_version():
    """Use mercurial data to compute version"""
    def version_scheme(version):
        return VERSION.replace('D', '.dev0')

    def local_scheme(version):
        return "+{rev}.{distance}".format(
            rev=version.node[1:],
            distance=version.distance)

    return {
        'version_scheme': version_scheme,
        'local_scheme': local_scheme
    }


setup(
    name=NAME,
    version=VERSION,
    description="Libervia multipurpose and multi frontend XMPP client",
    long_description="Libervia is a XMPP client based on a daemon/frontend "
                     "architecture. It's multi frontend (desktop, web, console "
                     "interface, CLI, etc) and multipurpose (instant messaging, "
                     "microblogging, games, file sharing, etc).",
    author="Association « Salut à Toi »",
    author_email="contact@goffi.org",
    url="https://salut-a-toi.org",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Twisted",
        "License :: OSI Approved :: GNU Affero General Public License v3 "
        "or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Communications :: Chat"
    ],
    packages=find_packages() + ["twisted.plugins"],
    data_files=[("share/locale/fr/LC_MESSAGES",
                 ["i18n/fr/LC_MESSAGES/sat.mo"]),
                (os.path.join("share/doc", NAME),
                 ["CHANGELOG", "COPYING", "INSTALL", "README", "README4TRANSLATORS"]),
                (os.path.join("share", DBUS_DIR), [DBUS_FILE]),
                ],
    entry_points={
        "console_scripts": [
            # backend + alias
            "libervia-backend = sat.core.launcher:Launcher.run",
            "sat = sat.core.launcher:Launcher.run",

            # CLI + aliases
            "libervia-cli = sat_frontends.jp.base:LiberviaCli.run",
            "li = sat_frontends.jp.base:LiberviaCli.run",
            "jp = sat_frontends.jp.base:LiberviaCli.run",

            # TUI + alias
            "libervia-tui = sat_frontends.primitivus.base:PrimitivusApp.run",
            "primitivus = sat_frontends.primitivus.base:PrimitivusApp.run",
            ],
        },
    zip_safe=False,
    setup_requires=["setuptools_scm"] if is_dev_version else [],
    use_scm_version=sat_dev_version if is_dev_version else False,
    install_requires=install_requires,
    extras_require=extras_require,
    package_data={"sat": ["VERSION"]},
    python_requires=">=3.7",
)
