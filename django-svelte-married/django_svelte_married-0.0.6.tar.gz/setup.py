# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_svelte_married',
 'django_svelte_married.management',
 'django_svelte_married.management.commands',
 'django_svelte_married.templatetags',
 'django_svelte_married.tests']

package_data = \
{'': ['*'], 'django_svelte_married': ['js/*', 'static/svelte/*', 'templates/*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'django-svelte-married',
    'version': '0.0.6',
    'description': 'JGM stands for "Just-Got-Married", because Django and Svelte is a perfect match 🤵👰.',
    'long_description': None,
    'author': 'niespodd',
    'author_email': 'dariusz@ticketwhat.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
