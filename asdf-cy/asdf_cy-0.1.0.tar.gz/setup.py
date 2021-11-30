# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asdf_cy']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.24,<0.30.0', 'numpy>=1.21.4,<2.0.0']

setup_kwargs = {
    'name': 'asdf-cy',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'reona',
    'author_email': 'c0116129a7@edu.teu.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
