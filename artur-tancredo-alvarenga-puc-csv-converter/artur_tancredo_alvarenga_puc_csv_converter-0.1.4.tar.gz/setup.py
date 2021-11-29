# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['artur_tancredo_alvarenga_puc_csv_converter']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pandas>=1.3.4,<2.0.0']

entry_points = \
{'console_scripts': ['csv_converter = '
                     'artur_tancredo_alvarenga_puc_csv_converter.converter:converter']}

setup_kwargs = {
    'name': 'artur-tancredo-alvarenga-puc-csv-converter',
    'version': '0.1.4',
    'description': 'Trabalho da PUC - converter csv para json e json para csv',
    'long_description': '',
    'author': 'Artur',
    'author_email': 'arturalvarenga@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.10,<4.0.0',
}


setup(**setup_kwargs)
