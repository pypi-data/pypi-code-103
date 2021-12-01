# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory', 'understory.apps.text_reader']

package_data = \
{'': ['*']}

install_requires = \
['microsub>=0.0.3,<0.0.4', 'understory>=0,<1']

entry_points = \
{'web.apps': ['text_reader = understory.apps.text_reader:app']}

setup_kwargs = {
    'name': 'understory-text-reader',
    'version': '0.0.2',
    'description': 'A text reader for the Understory framework.',
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
