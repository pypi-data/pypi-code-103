# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eagers',
 'eagers.basic',
 'eagers.class_definition',
 'eagers.config',
 'eagers.forecasting',
 'eagers.plot',
 'eagers.read',
 'eagers.setup',
 'eagers.simulate',
 'eagers.solver',
 'eagers.update',
 'eagers.write']

package_data = \
{'': ['*'], 'eagers': ['demo_files/*']}

install_requires = \
['ecos>=2.0.7,<3.0.0',
 'matplotlib>=3.1.1,<4.0.0',
 'numpy>=1.16.4,<2.0.0',
 'openpyxl>=3.0.3,<4.0.0',
 'scipy>=1.3.1,<2.0.0',
 'tables>=3.6.1,<4.0.0']

extras_require = \
{'building-plus': ['building-plus>=0.1.6,<0.2.0']}

setup_kwargs = {
    'name': 'eagers',
    'version': '0.4.1',
    'description': 'Efficient Allocation of Grid Energy Resources including Storage',
    'long_description': None,
    'author': 'Dustin McLarty',
    'author_email': 'dustin.mclarty@wsu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
