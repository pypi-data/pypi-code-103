# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['axu']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'axu',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'John Joy',
    'author_email': 'jk@axu.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
