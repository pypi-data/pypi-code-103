# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splunkautomator']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.13.0,<3.0.0']

setup_kwargs = {
    'name': 'splunkautomator',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'PeterWeiderer',
    'author_email': 'peter.weiderer@bmw.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
