# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['neuro_bump_version']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<8.1.0', 'packaging>=21.3,<22.0']

entry_points = \
{'console_scripts': ['neuro-bump-version = neuro_bump_version.main:main']}

setup_kwargs = {
    'name': 'neuro-bump-version',
    'version': '21.12.5',
    'description': 'Bump version for Neu.ro projects',
    'long_description': '# neuro-bump-version\nBump neu-ro tag to the next version\n\n\n## Installation\n\nInstall with [pipx](https://pypa.github.io/pipx/) in *user* space to access the tool\neverywhere:\n\n```\n$ pipx install neuro-bump-version\n```\n\n## Usage\n\n1. Change the current folder to cloned git project (or a subfolder).\n\n2. Run `neuro-bump-version` to create a next tag using Neu.ro versioning schema (see below).\n   Only projects with `use_scm_version` configured are supported.\n\n\n## Versioning schema\n\nThe schema should conform SemVer, CalVer, and Python PEP 440.\n\nWe use `YY.MM(.NN)` naming where `YY` is the last 2 digits of year, `MM` is the month\nnumber without trailing zero, NN is an incremental number instead, resetting this number\nto zero every month.\n\nZero incremental number is omitted.\n\nFor example, the first release in October will be `21.10` (implicit trailing zero),\nthe next is `21.10.1`, `21.10.2` and so on until November.\nThe first release in November should be `21.11`.\n',
    'author': 'Andrew Svetlov',
    'author_email': 'andrew.svetlov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/neuro-inc/neuro-bump-version',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
