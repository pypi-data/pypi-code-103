# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minimalist']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0', 'numpy>=1.21.4,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'minimalist',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Mehrdad Yazdani',
    'author_email': 'myazdani@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
