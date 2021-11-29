# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jalali_pandas']

package_data = \
{'': ['*']}

install_requires = \
['jdatetime>=3.6.4,<4.0.0']

setup_kwargs = {
    'name': 'jalali-pandas',
    'version': '0.1.1',
    'description': 'A Pandas extension to make work with Jalali Date easier.',
    'long_description': None,
    'author': 'Mehdi Ghodsizadeh',
    'author_email': 'mehdi.ghodsizadeh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
