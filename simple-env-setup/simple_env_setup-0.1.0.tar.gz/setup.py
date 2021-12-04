# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_env_setup',
 'simple_env_setup.recipes',
 'simple_env_setup.resources',
 'simple_env_setup.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'shutils>=0.1.0,<0.2.0', 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['setup_env = simple_env_setup.main:main']}

setup_kwargs = {
    'name': 'simple-env-setup',
    'version': '0.1.0',
    'description': 'Sets up the development environment to your (my) likings.',
    'long_description': None,
    'author': 'Peter Yuen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
