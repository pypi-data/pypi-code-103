# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['psme', 'psme.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'psme',
    'version': '0.1.0',
    'description': 'Python subcommands made easy.',
    'long_description': '',
    'author': 'Clay McLeod',
    'author_email': 'clay.l.mcleod@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
