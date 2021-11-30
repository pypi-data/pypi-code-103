# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nav_components']

package_data = \
{'': ['*']}

install_requires = \
['cython>=0.29.24,<0.30.0', 'numpy>=1.21.2,<2.0.0']

setup_kwargs = {
    'name': 'nav-components',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'wwwshwww',
    'author_email': 'www.shinderu.www@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
