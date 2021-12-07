# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['finpack', 'finpack.core', 'finpack.reports']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['finpack = finpack.core.cli:main']}

setup_kwargs = {
    'name': 'finpack',
    'version': '0.1.1',
    'description': 'Super simple financial tracking and management tools.',
    'long_description': None,
    'author': 'rackreaver',
    'author_email': 'rackreaver@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
