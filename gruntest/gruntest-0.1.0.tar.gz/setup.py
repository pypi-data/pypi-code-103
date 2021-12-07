# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gruntest']

package_data = \
{'': ['*']}

install_requires = \
['allure-pytest>=2.9.45,<3.0.0',
 'jsonpath>=0.82,<0.83',
 'pytest>=6.2.5,<7.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'gruntest',
    'version': '0.1.0',
    'description': 'graphql & restful / http(s) tools',
    'long_description': None,
    'author': 'zy7y',
    'author_email': '396667207@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
