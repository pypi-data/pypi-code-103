# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['caql']

package_data = \
{'': ['*']}

install_requires = \
['pkginfo>=1.7,<2.0']

setup_kwargs = {
    'name': 'caql',
    'version': '0.8.0',
    'description': 'Tell your front-end team they have a perfectly good graph query language at home',
    'long_description': None,
    'author': 'ExplosionAI GmbH',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.10',
}


setup(**setup_kwargs)
