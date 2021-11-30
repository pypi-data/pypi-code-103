# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edeta']

package_data = \
{'': ['*'], 'edeta': ['.ipynb_checkpoints/*']}

install_requires = \
['deta>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'edeta',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'arantesdv',
    'author_email': 'arantesdv@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
