# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fluss', 'fluss.graphql', 'fluss.graphql.mutations', 'fluss.graphql.queries']

package_data = \
{'': ['*']}

install_requires = \
['herre>=0.1.55,<0.2.0']

setup_kwargs = {
    'name': 'fluss',
    'version': '0.1.19',
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
