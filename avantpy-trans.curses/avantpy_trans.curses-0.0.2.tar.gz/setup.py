# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avantpy_trans', 'avantpy_trans.curses']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0']

setup_kwargs = {
    'name': 'avantpy-trans.curses',
    'version': '0.0.2',
    'description': 'avantpy translations',
    'long_description': None,
    'author': 'Phil Weir',
    'author_email': 'phil.t.weir@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
