# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['supermodels']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'supermodels',
    'version': '0.1.7',
    'description': '',
    'long_description': None,
    'author': 'Tsvetan Kintisheff',
    'author_email': 'kintisheff@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
