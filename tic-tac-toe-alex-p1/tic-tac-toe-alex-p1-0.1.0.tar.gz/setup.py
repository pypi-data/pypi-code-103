# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['logic']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tic-tac-toe-alex-p1',
    'version': '0.1.0',
    'description': 'Onboarding project phase 1',
    'long_description': None,
    'author': 'Alexandre Meneses',
    'author_email': 'alexandre.meneses@fabamaq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
