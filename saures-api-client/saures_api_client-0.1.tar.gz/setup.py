# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saures_api_client']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'saures-api-client',
    'version': '0.1',
    'description': 'SAURES API client',
    'long_description': None,
    'author': 'Yury Sokov',
    'author_email': 'yury@yurzs.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
