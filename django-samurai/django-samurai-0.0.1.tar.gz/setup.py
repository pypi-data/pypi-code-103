# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['samurai']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-samurai',
    'version': '0.0.1',
    'description': '?',
    'long_description': None,
    'author': 'c4ffein',
    'author_email': 'c4ffein.work@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
