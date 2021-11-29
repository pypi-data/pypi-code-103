# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyobs_aravis']

package_data = \
{'': ['*']}

install_requires = \
['PyGObject>=3.42,<4.0', 'numpy>=1.21,<2.0']

setup_kwargs = {
    'name': 'pyobs-aravis',
    'version': '0.14.1',
    'description': 'pyobs module for Aravis cameras',
    'long_description': None,
    'author': 'Tim-Oliver Husser',
    'author_email': 'thusser@uni-goettingen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
