# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bwrap']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bwrap = bwrap.core:main']}

setup_kwargs = {
    'name': 'bwrap',
    'version': '0.0.0',
    'description': 'A basic python binary wrapper.',
    'long_description': 'None',
    'author': 'Mark Beacom',
    'author_email': 'm@beacom.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
