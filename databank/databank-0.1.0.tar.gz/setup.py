# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['databank']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy>=1.4.27,<2.0.0']

setup_kwargs = {
    'name': 'databank',
    'version': '0.1.0',
    'description': 'tba',
    'long_description': None,
    'author': 'snapADDY GmbH',
    'author_email': 'info@snapaddy.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
