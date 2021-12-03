# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spylib', 'spylib.oauth', 'spylib.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'fastapi>=0.65.1,<0.66.0',
 'httpx>=0.18.1,<0.19.0',
 'loguru>=0.5.3,<0.6.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'shortuuid>=1.0.1,<2.0.0',
 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'spylib',
    'version': '0.3.2',
    'description': "A library to facilitate interfacing with Shopify's API",
    'long_description': None,
    'author': 'Anthony Hillairet',
    'author_email': 'ant@satel.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
