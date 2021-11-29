# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['building_plus',
 'building_plus.basic',
 'building_plus.components',
 'building_plus.config',
 'building_plus.process',
 'building_plus.read']

package_data = \
{'': ['*'], 'building_plus': ['demo_files/*']}

install_requires = \
['matplotlib>=3.1.1,<4.0.0', 'numpy>=1.16.4,<2.0.0', 'scipy>=1.3.1,<2.0.0']

setup_kwargs = {
    'name': 'building-plus',
    'version': '0.1.7',
    'description': 'Dynamic building simulator based on EnergyPlus with enhancements.',
    'long_description': None,
    'author': 'Dustin McLarty',
    'author_email': 'dustin.mclarty@wsu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
