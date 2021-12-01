# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canopy', 'canopy.templates']

package_data = \
{'': ['*'], 'canopy': ['static/*']}

install_requires = \
['understory-indieauth-client>=0.0.4,<0.0.5',
 'understory-indieauth-server>=0.0.4,<0.0.5',
 'understory-micropub-server>=0.0.4,<0.0.5',
 'understory-microsub-server>=0.0.2,<0.0.3',
 'understory-text-editor>=0.0.4,<0.0.5',
 'understory-text-reader>=0.0.2,<0.0.3',
 'understory-tracker>=0.0.2,<0.0.3',
 'understory-webmention-endpoint>=0.0.3,<0.0.4',
 'understory-websub-endpoint>=0.0.3,<0.0.4',
 'understory>=0,<1']

setup_kwargs = {
    'name': 'canopy-platform',
    'version': '0.0.2',
    'description': 'A decentralized social platform.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
