# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['microsub']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0,<1']

setup_kwargs = {
    'name': 'microsub',
    'version': '0.0.3',
    'description': 'A library for writing Microsub servers and clients.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
