# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['breno-csv-converter']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['csv_converter = breno-csv-converter.converter:converter']}

setup_kwargs = {
    'name': 'breno-csv-converter',
    'version': '0.1.0',
    'description': 'Convert csv to json and vice versa.',
    'long_description': '',
    'author': 'Breno M L Costa',
    'author_email': 'brenomlomasso@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
