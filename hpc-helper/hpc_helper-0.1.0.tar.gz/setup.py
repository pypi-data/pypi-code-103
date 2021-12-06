# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hpc_helper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hpc-helper',
    'version': '0.1.0',
    'description': "Python package with helper functions for working with FAU's High Performance Cluster (HPC).",
    'long_description': None,
    'author': 'Robert Richer',
    'author_email': 'robert.richer@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
