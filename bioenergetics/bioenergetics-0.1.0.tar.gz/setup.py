# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bioenergetics']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pytest>=6.2.5,<7.0.0',
 'scipy>=1.7.3,<2.0.0']

setup_kwargs = {
    'name': 'bioenergetics',
    'version': '0.1.0',
    'description': 'Combined bioenergetics and visual foraging model',
    'long_description': None,
    'author': 'Chee Sing Lee',
    'author_email': 'cheesinglee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
