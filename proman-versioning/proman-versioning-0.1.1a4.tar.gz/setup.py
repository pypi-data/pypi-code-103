# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proman_versioning', 'proman_versioning.cli', 'proman_versioning.grammars']

package_data = \
{'': ['*'], 'proman_versioning': ['templates/*']}

install_requires = \
['argufy>=0.1.1-alpha.12,<0.2.0',
 'cffi>=1.15.0,<2.0.0',
 'compendium>=0.1.1-alpha.2,<0.2.0',
 'jinja2>=2.11.2,<3.0.0',
 'lark-parser>=0.10.0,<0.11.0',
 'packaging>=20.9,<21.0',
 'pygit2>=1.6.1,<2.0.0',
 'transitions>=0.8.4,<0.9.0']

entry_points = \
{'console_scripts': ['proman-version = proman_versioning.__main__:main',
                     'vers = proman_versioning.__main__:main',
                     'version = proman_versioning.__main__:main']}

setup_kwargs = {
    'name': 'proman-versioning',
    'version': '0.1.1a4',
    'description': 'Project Manager Versioning tool.',
    'long_description': '# Proman Versioning\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://spdx.org/licenses/MPL-2.0)\n[![Build Status](https://travis-ci.org/kuwv/proman-versioning.svg?branch=master)](https://travis-ci.org/kuwv/proman-versioning)\n[![codecov](https://codecov.io/gh/kuwv/proman-versioning/branch/master/graph/badge.svg)](https://codecov.io/gh/kuwv/proman-versioning)\n\n## Overview\n\nProject Manager Versioning tool.\n\n## Install\n\n`pip install proman-versioning`\n\n## Setup\n\n```\n[tool.proman.versioning]\nenable_devreleases = true\nenable_prereleases = true\nenable_postreleases = true\n\n[[tool.proman.versioning.files]]\nfilepath = "example/__init__.py"\npattern = "__version__ = \'${version}\'"\n\n[[tool.proman.versioning.files]]\nfilepath = "pyproject.toml"\npattern = "version = \\"${version}\\""\n```\n',
    'author': 'Jesse P. Johnson',
    'author_email': 'jpj6652@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
