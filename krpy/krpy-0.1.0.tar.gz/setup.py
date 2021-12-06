# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['krpy']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'scipy>=1.7.2,<2.0.0',
 'seaborn>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'krpy',
    'version': '0.1.0',
    'description': 'Relative Permeabilities Utility Tool',
    'long_description': None,
    'author': 'Santiago Cuervo',
    'author_email': 'scuervo91@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
