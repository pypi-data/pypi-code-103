# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.mypy']

package_data = \
{'': ['*']}

install_requires = \
['autohooks>=21.7.0,<22.0.0']

setup_kwargs = {
    'name': 'autohooks-plugin-mypy',
    'version': '0.1.4',
    'description': 'An autohooks plugin for python code static typing check with mypy',
    'long_description': None,
    'author': 'Vincent Texier',
    'author_email': 'vit@free.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
