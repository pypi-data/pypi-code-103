# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trapdoor', 'trapdoor.tests', 'trapdoor.utils']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'trapdoor',
    'version': '0.5.0',
    'description': 'Turn-key configuration file management for Python packages.',
    'long_description': None,
    'author': 'Clay McLeod',
    'author_email': 'clay.l.mcleod@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
