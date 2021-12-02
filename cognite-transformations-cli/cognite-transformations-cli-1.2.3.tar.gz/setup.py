# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['cognite',
 'cognite.transformations_cli',
 'cognite.transformations_cli.commands',
 'cognite.transformations_cli.commands.deploy']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'cognite-extractor-utils>=1.5.2,<2.0.0',
 'cognite-sdk-experimental>=0.60.28,<0.61.0',
 'sqlparse>=0.4.2,<0.5.0',
 'tabulate>=0.8.9,<0.9.0',
 'types-retry>=0.1.5,<0.2.0',
 'types-tabulate>=0.8.3,<0.9.0']

entry_points = \
{'console_scripts': ['transformations-cli = '
                     'cognite.transformations_cli.__main__:main']}

setup_kwargs = {
    'name': 'cognite-transformations-cli',
    'version': '1.2.3',
    'description': 'A CLI for the Transformations service in CDF',
    'long_description': '<a href="https://cognite.com/">\n    <img src="https://github.com/cognitedata/cognite-python-docs/blob/master/img/cognite_logo.png" alt="Cognite logo" title="Cognite" align="right" height="80" />\n</a>\n\nCognite Python `transformations-cli`\n================================\n[![Build Status](https://github.com/cognitedata/transformations-cli/workflows/release/badge.svg)](https://github.com/cognitedata/transformations-cli/actions)\n[![Documentation Status](https://readthedocs.com/projects/cognite-transformations-cli/badge/?version=latest)](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/cognitedata/transformations-cli/branch/main/graph/badge.svg?token=PSkli74vvX)](https://codecov.io/gh/cognitedata/transformations-cli)\n[![PyPI version](https://badge.fury.io/py/cognite-transformations-cli.svg)](https://pypi.org/project/cognite-transformations-cli)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cognite-transformations-cli)\n[![License](https://img.shields.io/github/license/cognitedata/python-extractor-utils)](LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n# Transformations CLI\n\nThe Transormations CLI is a replacement for [jetfire-cli](https://github.com/cognitedata/jetfire-cli) rewritten on top\nof the new Python SDK for Transformations.\n\n### CLI Documentation\n\nDocumentation for CLI is hosted [here](https://cognite-transformations-cli.readthedocs-hosted.com/en/latest/).\n\n### GitHub Action\n\n`transformations-cli` also provides a GitHub Action which can be used to deploy transformations. You can find the documentation for transformations-cli GitHub Action [here](githubaction.md).\n\n\n### GitHub Action Migration: jetfire-cli@v2 to transformations-cli@main\n\nIf you\'ve already used the old `jetfire-cli` in a GitHub Action we recommend you migrate to the new GitHub Action. You can find the migration guide [here](migrationguide.md).\n\n### Contributing\n\nWe use [poetry](https://python-poetry.org) to manage dependencies and to administrate virtual environments. To develop\n`transformations-cli`, follow the following steps to set up your local environment:\n\n 1. Install poetry: (add `--user` if desirable)\n    ```\n    $ pip install poetry\n    ```\n 2. Clone repository:\n    ```\n    $ git clone git@github.com:cognitedata/transformations-cli.git\n    ```\n 3. Move into the newly created local repository:\n    ```\n    $ cd transformations-cli\n    ```\n 4. Create virtual environment and install dependencies:\n    ```\n    $ poetry install\n    ```\n\nAll code must pass [black](https://github.com/ambv/black) and [isort](https://github.com/timothycrosley/isort) style\nchecks to be merged. It is recommended to install pre-commit hooks to ensure this locally before commiting code:\n\n```\n$ poetry run pre-commit install\n```\n\nTo publish a new version change the version in `cognite/transformations_cli/__init__.py` and `pyproject.toml`. Also, remember to add an entry to `CHANGELOG`.\n\nThis project adheres to the [Contributor Covenant v2.0](https://www.contributor-covenant.org/version/2/0/code_of_conduct/)\nas a code of conduct.\n\n\n',
    'author': 'Mathias Lohne',
    'author_email': 'mathias.lohne@cognite.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cognitedata/transformations-cli',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
