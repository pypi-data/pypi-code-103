# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wkfs_wrapper']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'wkfs-wrapper',
    'version': '0.1.0',
    'description': 'WKFS wrapper to generate documents from WKFS system',
    'long_description': None,
    'author': 'Tejas Bhandari',
    'author_email': 'tejas@thesummitgrp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
