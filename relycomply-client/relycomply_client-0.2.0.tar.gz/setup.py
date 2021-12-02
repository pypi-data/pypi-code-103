# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['relycomply_client']

package_data = \
{'': ['*']}

install_requires = \
['boto3',
 'dryenv',
 'gql==3.0.0a1',
 'littleutils',
 'pandas',
 'requests',
 'requests-toolbelt']

setup_kwargs = {
    'name': 'relycomply-client',
    'version': '0.2.0',
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
