# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_pydantic_vault']

package_data = \
{'': ['*']}

install_requires = \
['async-hvac==0.6.1',
 'nest-asyncio>=1.5.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'async-pydantic-vault',
    'version': '0.1.9',
    'description': 'A simple extension to Pydantic BaseSettings that can retrieve secrets from Hashicorp Vault using Async',
    'long_description': '# Async Pydantic Vault',
    'author': 'Adolfo Villalobos',
    'author_email': 'amvillalobos@uc.cl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AdolfoVillalobos/async-pydantic-vault',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
