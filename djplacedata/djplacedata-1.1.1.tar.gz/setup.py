# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djplacedata', 'djplacedata.management.commands', 'djplacedata.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.0',
 'census-shapefiles==1.1.2',
 'census>=0.8.18,<0.9.0',
 'sodapy>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'djplacedata',
    'version': '1.1.1',
    'description': '',
    'long_description': None,
    'author': 'Zach Perkitny',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
