# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fvidal_packages',
 'fvidal_packages.db_api_client',
 'fvidal_packages.stock_utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy==1.4.27',
 'kaleido==0.2.1',
 'pandas==1.3.4',
 'plotly>=5.4.0,<6.0.0',
 'psycopg2-binary==2.9.2',
 'requests==2.26.0']

setup_kwargs = {
    'name': 'itba-cde-tpf-python-applications-fvidal90',
    'version': '1.2.2',
    'description': 'TP Vidal',
    'long_description': None,
    'author': 'Fernando Vidal',
    'author_email': 'picovidal22@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
