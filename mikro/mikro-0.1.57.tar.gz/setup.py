# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mikro', 'mikro.graphql', 'mikro.graphql.mutations', 'mikro.graphql.queries']

package_data = \
{'': ['*']}

install_requires = \
['dask==2021.11.2',
 'docstring-parser>=0.10,<0.11',
 'herre>=0.1.58,<0.2.0',
 'inflection>=0.5.1,<0.6.0',
 'pandas>=1.3.4,<2.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 's3fs>=2021.9.0,<2022.0.0',
 'xarray>=0.19.0,<0.20.0',
 'zarr==2.8.3']

setup_kwargs = {
    'name': 'mikro',
    'version': '0.1.57',
    'description': 'images for arnheim',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
