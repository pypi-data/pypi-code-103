# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['buffy']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0']

setup_kwargs = {
    'name': 'buffy-server',
    'version': '0.1.0',
    'description': 'Shared framebuffer chat server',
    'long_description': None,
    'author': 'Ossi Rajuvaara',
    'author_email': 'ossi@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
