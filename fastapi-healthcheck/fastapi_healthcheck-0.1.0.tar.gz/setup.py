# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_healthcheck']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0']

setup_kwargs = {
    'name': 'fastapi-healthcheck',
    'version': '0.1.0',
    'description': 'Base package to handle health checks with FastAPI.',
    'long_description': None,
    'author': 'James Tombleson',
    'author_email': 'luther38@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
