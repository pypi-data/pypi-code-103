# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saiph', 'saiph.reduction', 'saiph.reduction.utils']

package_data = \
{'': ['*']}

install_requires = \
['flake8>=4.0.1,<5.0.0',
 'matplotlib>=3.4,<4.0',
 'numpy>=1.21,<2.0',
 'pandas>=1.3,<2.0',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.7,<2.0']

setup_kwargs = {
    'name': 'saiph',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'Zineb Bennis',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
