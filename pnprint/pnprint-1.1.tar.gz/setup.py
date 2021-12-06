# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pnprint']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pnprint',
    'version': '1.1',
    'description': 'format and color serialized data strings, to make them more human readable',
    'long_description': None,
    'author': 'jimy byerley',
    'author_email': 'jimy.byerley@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.2,<4.0',
}


setup(**setup_kwargs)
