# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docgen']

package_data = \
{'': ['*']}

install_requires = \
['robotframework>=3.2.2,<5']

entry_points = \
{'console_scripts': ['docgen = docgen.cli:run']}

setup_kwargs = {
    'name': 'robotframework-docgen',
    'version': '0.13.0',
    'description': 'Robot Framework documentation finder and generator',
    'long_description': '',
    'author': 'Ossi Rajuvaara',
    'author_email': 'ossi@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/robocorp/robotframework-docgen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
