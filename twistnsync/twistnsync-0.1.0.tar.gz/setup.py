# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twistnsync']

package_data = \
{'': ['*']}

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.16.0,<0.17.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

setup_kwargs = {
    'name': 'twistnsync',
    'version': '0.1.0',
    'description': 'Twist-n-Sync is time synchronization algorithm that employs IMU gyroscope data.',
    'long_description': '# Twist-n-Sync\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/twistnsync">\n    <img src="https://img.shields.io/pypi/v/twistnsync.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/MobileRoboticsSkoltech/twistnsync/actions">\n    <img src="https://github.com/MobileRoboticsSkoltech/twistnsync/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<a href="https://twistnsync.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/twistnsync/badge/?version=latest" alt="Documentation Status">\n</a>\n\n<a href="https://pyup.io/repos/github/MobileRoboticsSkoltech/twistnsync/">\n<img src="https://pyup.io/repos/github/MobileRoboticsSkoltech/twistnsync/shield.svg" alt="Updates">\n</a>\n\n</p>\n\n\nTwist-n-Sync is time synchronization algorithm that employs IMU gyroscope data\n\n\n* Free software: Apache-2.0\n* Documentation: <https://twistnsync.readthedocs.io>\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Marsel Faizullin',
    'author_email': 'marsel.faizullin@skoltech.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MobileRoboticsSkoltech/twistnsync',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
