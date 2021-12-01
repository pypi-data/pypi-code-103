# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_query_planning']

package_data = \
{'': ['*']}

install_requires = \
['PyMonad>=2.4.0,<3.0.0',
 'SQLAlchemy>=1.4.27,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'networkx>=2.6.3,<3.0.0',
 'psycopg2>=2.9.2,<3.0.0',
 'pydot>=1.4.2,<2.0.0',
 'toolz>=0.11.2,<0.12.0']

entry_points = \
{'console_scripts': ['vqp = views_query_planning.cli:vqp']}

setup_kwargs = {
    'name': 'views-query-planning',
    'version': '1.3.0',
    'description': '',
    'long_description': None,
    'author': 'peder2911',
    'author_email': 'pglandsverk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
