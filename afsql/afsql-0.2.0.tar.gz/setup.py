# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['afsql']

package_data = \
{'': ['*']}

install_requires = \
['DBUtils>=2.0,<3.0',
 'PyMySQL>=1.0.2,<2.0.0',
 'neo4j>=4.2.1,<5.0.0',
 'psycopg2-binary>=2.8.6,<3.0.0',
 'py2neo>=2021.2.3,<2022.0.0']

setup_kwargs = {
    'name': 'afsql',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Asdil',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
