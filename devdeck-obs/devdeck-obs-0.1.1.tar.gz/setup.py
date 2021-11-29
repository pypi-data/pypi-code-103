# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['devdeck_obs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'devdeck-obs',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Tom Whitwell',
    'author_email': 'tom@whi.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
