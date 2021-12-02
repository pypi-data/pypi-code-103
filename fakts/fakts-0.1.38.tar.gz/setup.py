# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fakts',
 'fakts.beacon',
 'fakts.cli',
 'fakts.config',
 'fakts.grants',
 'fakts.grants.cli',
 'fakts.grants.meta',
 'fakts.grants.qt',
 'fakts.middleware',
 'fakts.middleware.environment']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.2',
 'QtPy>=1.11.2,<2.0.0',
 'koil>=0.1.58,<0.2.0',
 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'fakts',
    'version': '0.1.38',
    'description': 'easy configuration discovery based on UDP broadcasts and konfig beacons (servers that redirect configs back to the client)',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
