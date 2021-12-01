# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['caujax']

package_data = \
{'': ['*']}

install_requires = \
['jax>=0.2.25,<0.3.0']

setup_kwargs = {
    'name': 'caujax',
    'version': '0.1.1',
    'description': 'Causal Jax',
    'long_description': '# caujax',
    'author': 'Jeong-Yoon Lee',
    'author_email': 'jeongyoon.lee1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/caujax/caujax',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
