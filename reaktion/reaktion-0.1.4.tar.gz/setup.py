# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reaktion',
 'reaktion.atoms',
 'reaktion.atoms.arkitekt',
 'reaktion.atoms.reactive',
 'reaktion.atoms.reactive.combinators']

package_data = \
{'': ['*']}

install_requires = \
['arkitekt>=0.1.104,<0.2.0', 'fluss>=0.1.19,<0.2.0']

setup_kwargs = {
    'name': 'reaktion',
    'version': '0.1.4',
    'description': '',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
