# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_svelte_married']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-svelte-married',
    'version': '0.0.1',
    'description': 'JGM stands for "Just-Got-Married", because Django and Svelte is a perfect match 🤵👰.',
    'long_description': None,
    'author': 'niespodd',
    'author_email': 'dariusz@ticketwhat.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
