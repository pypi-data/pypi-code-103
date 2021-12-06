#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

VERSION = "1.0.0"
setup(
    name="still-rm",
    packages=["still_rm"],
    version=VERSION,
    description="A utility for removing still frames from video files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chiao",
    author_email="php@html.js.cn",
    url="https://github.com/joy2fun/still-rm",
    keywords=[],
    classifiers=[],
    install_requires=[
        'opencv-python>=4.0',
        'ffmpeg-python>=0.1'
    ],
    entry_points={
        "console_scripts": ["still-rm = still_rm.__main__:main"]
    },
)
