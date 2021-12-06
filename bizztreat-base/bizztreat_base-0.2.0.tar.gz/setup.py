# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bizztreat_base', 'bizztreat_base.utils']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'bizztreat-base',
    'version': '0.2.0',
    'description': 'Set of helpers to help you build Bizzflow components easily',
    'long_description': None,
    'author': 'Tomas Votava',
    'author_email': 'tomas.votava@bizztreat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
