# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noll']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'noll',
    'version': '0.0.0',
    'description': '',
    'long_description': '# Noll',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/deepadmax/noll',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
