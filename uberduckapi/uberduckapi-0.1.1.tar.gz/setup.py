# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uberduckapi']

package_data = \
{'': ['*']}

install_requires = \
['polling>=0.3.2,<0.4.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'uberduckapi',
    'version': '0.1.1',
    'description': 'Python wrapper for uberduck API',
    'long_description': None,
    'author': 'George',
    'author_email': 'mazzeogeorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
