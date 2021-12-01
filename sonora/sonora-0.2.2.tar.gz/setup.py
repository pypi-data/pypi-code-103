# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sonora']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0',
 'async-timeout>=3.0.1,<5',
 'grpcio>=1.37.1,<2.0.0',
 'urllib3>=1.26.4,<2.0.0']

setup_kwargs = {
    'name': 'sonora',
    'version': '0.2.2',
    'description': 'A WSGI and ASGI compatible grpc-web implementation.',
    'long_description': None,
    'author': 'Alex Stapleton',
    'author_email': 'alexs@prol.etari.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/public/sonora',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
