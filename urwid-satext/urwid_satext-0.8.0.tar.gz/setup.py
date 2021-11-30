#!/usr/bin/env python3

from setuptools import setup
from glob import glob

name = "urwid_satext"

setup(
    name=name,
    version="0.8.0",
    description="SàT extension widgets for Urwid",
    long_description=(
        "Urwid SàT extension widgets is a set of widgets for the console "
        "user interface library Urwid (http://excess.org/urwid/). This "
        'library, originaly made for the Libervia (formerly "SàT") project, was '
        "eventually separated so other softwares can use it. Widgets provided "
        "include password text box, tab container, dialogs, file chooser "
        "etc. Feel free to go to the project page for more informations."),
    author="Goffi (Jérôme Poisson)",
    author_email="goffi@goffi.org",
    url="https://wiki.goffi.org/w/index.php/Urwid-satext",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Intended Audience :: Developers",
    ],
    packages=["urwid_satext"],
    data_files=[
        (
            "share/locale/fr/LC_MESSAGES",
            ["i18n/fr/LC_MESSAGES/urwid_satext.mo"],
        ),
        ("share/doc/%s/examples" % name, glob("examples/*.py")),
        ("share/doc/%s" % name, ["COPYING", "COPYING.LESSER", "README", "CHANGELOG"]),
    ],
    install_requires=["urwid >= 1.2.0"],
)
