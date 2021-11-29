# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['maxipago',
 'maxipago.managers',
 'maxipago.managers.payment',
 'maxipago.requesters',
 'maxipago.requesters.payment',
 'maxipago.resources',
 'maxipago.utils']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.18,<3.0']

setup_kwargs = {
    'name': 'rede-cotabest',
    'version': '1.0.2',
    'description': '',
    'long_description': None,
    'author': 'Fernando Coutinho',
    'author_email': 'fernando.coutinho@cotabest.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
