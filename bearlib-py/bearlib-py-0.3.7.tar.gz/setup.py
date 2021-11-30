# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['bearlib', 'bearlib.logging', 'bearlib.notifiers', 'bearlib.oracle']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'bearlib-py',
    'version': '0.3.7',
    'description': 'A library of utilities and standardizations used for writing Python code for UNCO applications and scripts.',
    'long_description': None,
    'author': 'Zevaryx',
    'author_email': 'zevaryx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
