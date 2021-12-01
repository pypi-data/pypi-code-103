# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kuay', 'kuay.cli', 'kuay.graphql', 'kuay.graphql.queries']

package_data = \
{'': ['*']}

install_requires = \
['herre>=0.1.55,<0.2.0']

entry_points = \
{'console_scripts': ['kuay = kuay.cli.main:entrypoint']}

setup_kwargs = {
    'name': 'kuay',
    'version': '0.1.19',
    'description': '',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
