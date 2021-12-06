# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vimnote']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['vimnote = vimnote:main']}

setup_kwargs = {
    'name': 'vimnote',
    'version': '1.0.2',
    'description': 'a vim-based TUI notetaking application',
    'long_description': None,
    'author': 'maxcutlyp',
    'author_email': 'max@maxcutlyp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10',
}


setup(**setup_kwargs)
