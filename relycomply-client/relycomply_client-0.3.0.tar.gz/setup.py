# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['relycomply_client']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'Pygments>=2.10.0,<3.0.0',
 'boto3',
 'dryenv',
 'gql==3.0.0a1',
 'littleutils',
 'pandas',
 'requests',
 'requests-toolbelt',
 'tabulate>=0.8.9,<0.9.0',
 'termcolor>=1.1.0,<2.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'relycomply-client',
    'version': '0.3.0',
    'description': 'A python client for the RelyComply platform',
    'long_description': None,
    'author': 'James Saunders',
    'author_email': 'james@relycomply.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
