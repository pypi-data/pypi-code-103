# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mysql_handler']

package_data = \
{'': ['*']}

install_requires = \
['mysql-connector-python>=8.0.25,<9.0.0']

setup_kwargs = {
    'name': 'mysql-handler',
    'version': '1.1.1',
    'description': '',
    'long_description': None,
    'author': 'Amit Agrawal',
    'author_email': 'amitagrawalcs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
