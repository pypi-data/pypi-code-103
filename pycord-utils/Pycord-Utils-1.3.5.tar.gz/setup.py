"""
MIT License

Copyright (c) 2019-2020 PythonistaGuild
Copyright (c) 2021 Devon (Gorialis) R
Copyright (c) 2021 Pycord

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pathlib
# import re
import setuptools
from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = VersionInfo(major=1, minor=3, micro=5, releaselevel='final', serial=0)
__version__ = '.'.join(map(str, (version_info.major, version_info.minor, version_info.micro)))

ROOT = pathlib.Path(__file__).parent

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open(ROOT / "README.md", encoding="utf-8") as f:
    README = f.read()

VERSION = __version__

packages = [
        "pycord.ext.audio",
        "pycord.ext.ipc",
        "pycord.ext.alternatives",
        "pycord.ext.dl",
        "pycord.ext.dl.downloader",
        "pycord.ext.dl.extractor",
        "pycord.ext.dl.postprocessor",
        "pycord.features",
        "pycord.repl",
        "pycord.shim",
    ]

extras_require = {
    "voice": [
        "PyNaCl>=1.3.0,<1.5"
    ],
    "extra": [
        "braceexpand>=0.1.7",
        "click>=8.0.1",
        "import_expression>=1.0.0,<2.0.0",
        "importlib_metadata>=3.7.0",
    ],
    "docs": [
        "sphinx==4.3.1",
        "sphinxcontrib_trio==1.1.2",
        "sphinxcontrib-websupport",
    ],
    "speed": [
        "orjson>=3.5.4",
        "aiodns>=1.1",
        "Brotlipy",
        "cchardet",
    ],

}

setuptools.setup(
    name="Pycord-Utils",
    author="Pycord",
    url="https://github.com/pycord/utilitys",
    version=VERSION,
    packages=packages,
    license="MIT",
    description="Utility Plugin For Pycord",
    long_description=README,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
)
