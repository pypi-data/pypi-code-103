# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djangopyetl']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.1,<4.0',
 'SQLAlchemy>=1.4.26,<2.0.0',
 'ipython>=7.28.0,<8.0.0',
 'numpy>=1.21.3,<2.0.0',
 'pandas==1.3.4',
 'pyodbc>=4.0.32,<5.0.0']

setup_kwargs = {
    'name': 'djangopyetl',
    'version': '0.1.5',
    'description': 'Django app for ETL',
    'long_description': None,
    'author': 'MacSoares',
    'author_email': 'macario.junior@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
