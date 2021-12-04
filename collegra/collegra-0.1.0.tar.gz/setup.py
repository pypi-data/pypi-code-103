# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['collegra']

package_data = \
{'': ['*']}

install_requires = \
['pytest-cov>=3.0.0,<4.0.0', 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'collegra',
    'version': '0.1.0',
    'description': 'Collaborative Learning Graphs',
    'long_description': None,
    'author': 'Bob Kraft',
    'author_email': 'bkraft4257@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
