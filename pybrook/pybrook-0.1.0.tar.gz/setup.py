# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybrook']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pybrook',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Michał Rokita',
    'author_email': 'mrokita@mrokita.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
