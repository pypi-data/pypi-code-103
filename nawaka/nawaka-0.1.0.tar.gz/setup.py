# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nawaka', 'nawaka.groups']

package_data = \
{'': ['*']}

install_requires = \
['fuzzywuzzy>=0.18.0,<0.19.0',
 'loguru>=0.5.3,<0.6.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'simplekml>=1.3.6,<2.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['get_groups = nawaka.groups.get_group_location:cli']}

setup_kwargs = {
    'name': 'nawaka',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Tristan de Boer',
    'author_email': 'info@tristandeboer.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
