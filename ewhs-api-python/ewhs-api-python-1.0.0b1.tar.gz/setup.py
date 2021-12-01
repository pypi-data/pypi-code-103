# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ewhs']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'ewhs-api-python',
    'version': '1.0.0b1',
    'description': 'Python library for the eWarehousing Solutions API.',
    'long_description': None,
    'author': 'Liam Boer',
    'author_email': 'liamboer@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
