# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mgwrvisualizer']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mgwrvisualizer',
    'version': '0.0.1',
    'description': 'Visualization Suite for Multiscale Geographically Weighted Regression (MGWR) ',
    'long_description': '# MGWRVisualizer - Python Client\n\nWork in Progress\n',
    'author': 'Matthew Tralka',
    'author_email': 'matthew@tralka.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mtralka/MGWRVisualizer',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
