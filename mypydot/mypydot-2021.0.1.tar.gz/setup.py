# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mypydot']

package_data = \
{'': ['*'],
 'mypydot': ['template/*',
             'template/language/*',
             'template/language/go/*',
             'template/language/java/*',
             'template/language/python/*',
             'template/os/*',
             'template/shell/*',
             'template/tools/*']}

install_requires = \
['PyYAML==6.0']

setup_kwargs = {
    'name': 'mypydot',
    'version': '2021.0.1',
    'description': '',
    'long_description': None,
    'author': 'John Smith',
    'author_email': 'john@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
