# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory',
 'understory.apps.microsub_server',
 'understory.apps.microsub_server.templates']

package_data = \
{'': ['*']}

install_requires = \
['microsub>=0.0.3,<0.0.4', 'understory>=0,<1', 'websub-temporary>=0.0.3,<0.0.4']

entry_points = \
{'web.apps': ['microsub_server = understory.apps.microsub_server:app']}

setup_kwargs = {
    'name': 'understory-microsub-server',
    'version': '0.0.2',
    'description': 'A Microsub server for the Understory framework.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
