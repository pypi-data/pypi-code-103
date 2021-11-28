# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aria2_rpc_client']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'aria2-rpc-client',
    'version': '0.3.0',
    'description': 'Aria2 RPC Client',
    'long_description': None,
    'author': 'Özkan ŞEN',
    'author_email': 'ozkansen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
