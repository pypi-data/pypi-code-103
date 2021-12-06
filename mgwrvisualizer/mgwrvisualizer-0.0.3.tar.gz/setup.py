# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mgwrvisualizer']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0', 'pandas>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'mgwrvisualizer',
    'version': '0.0.3',
    'description': 'Visualization Suite for Multiscale Geographically Weighted Regression (MGWR) ',
    'long_description': '# MGWRVisualizer - Python Client\n\nWork in Progress\n',
    'author': 'Matthew Tralka',
    'author_email': 'matthew@tralka.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mtralka/MGWRVisualizer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
