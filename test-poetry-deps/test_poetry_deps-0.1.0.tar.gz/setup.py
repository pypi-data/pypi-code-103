# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['test_poetry_deps']

package_data = \
{'': ['*']}

install_requires = \
['emoji>=1.6.1,<2.0.0', 'numpy>=1.21.4,<2.0.0', 'pandas>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'test-poetry-deps',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Skylar Kerzner',
    'author_email': 'skerzner@community.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
