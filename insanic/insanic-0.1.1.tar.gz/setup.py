# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['insanic']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'insanic',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Dmitry Ovchinnikov',
    'author_email': 'mail@dimka.online',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
