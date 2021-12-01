# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_dataviz', 'views_dataviz.map', 'views_dataviz.map.presets']

package_data = \
{'': ['*'], 'views_dataviz.map': ['assets/*']}

install_requires = \
['contextily>=1.1.0,<2.0.0',
 'geopandas>=0.9.0,<0.10.0',
 'ipykernel>=6.4.1,<7.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'pandas>=1.3.2,<2.0.0']

setup_kwargs = {
    'name': 'views-dataviz',
    'version': '0.7.0',
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
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
