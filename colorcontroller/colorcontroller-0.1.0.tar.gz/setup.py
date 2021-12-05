# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colorcontroller']

package_data = \
{'': ['*'], 'colorcontroller': ['readmepics/*']}

install_requires = \
['Pillow==8.4.0',
 'cycler==0.11.0',
 'fonttools==4.28.3',
 'kiwisolver==1.3.2',
 'matplotlib==3.5.0',
 'numpy==1.21.4',
 'packaging==21.3',
 'pandas==1.3.4',
 'pyparsing==3.0.6',
 'python-dateutil==2.8.2',
 'pytz==2021.3',
 'setuptools-scm==6.3.2',
 'six==1.16.0',
 'tomli==1.2.2']

setup_kwargs = {
    'name': 'colorcontroller',
    'version': '0.1.0',
    'description': 'ColorController is a Pythonic interface for managing colors using either english-language names or one of several standard color values.',
    'long_description': None,
    'author': 'Tal Zaken',
    'author_email': 'talzaken@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
