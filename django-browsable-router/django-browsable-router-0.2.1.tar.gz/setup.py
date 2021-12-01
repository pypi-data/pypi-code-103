# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['browsable_router']

package_data = \
{'': ['*']}

install_requires = \
['Django>=1.10',
 'djangorestframework>=3.7.0',
 'typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'django-browsable-router',
    'version': '0.2.1',
    'description': 'A Django REST Framework router that can show APIViews and include other routers as navigable urls in the root view.',
    'long_description': '# Django Browsable Router\n\n[![Coverage Status](https://coveralls.io/repos/github/MrThearMan/django-browsable-router/badge.svg?branch=main)](https://coveralls.io/github/MrThearMan/django-browsable-router?branch=main)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/MrThearMan/django-browsable-router/Tests)](https://github.com/MrThearMan/django-browsable-router/actions/workflows/main.yml)\n[![PyPI](https://img.shields.io/pypi/v/django-browsable-router)](https://pypi.org/project/django-browsable-router)\n[![GitHub](https://img.shields.io/github/license/MrThearMan/django-browsable-router)](https://github.com/MrThearMan/django-browsable-router/blob/main/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/MrThearMan/django-browsable-router)](https://github.com/MrThearMan/django-browsable-router/commits/main)\n[![GitHub issues](https://img.shields.io/github/issues-raw/MrThearMan/django-browsable-router)](https://github.com/MrThearMan/django-browsable-router/issues)\n\n```shell\npip install django-browsable-router\n```\n---\n\n**Documentation**: [https://mrthearman.github.io/django-browsable-router/](https://mrthearman.github.io/django-browsable-router/)\n\n**Source Code**: [https://github.com/MrThearMan/django-browsable-router](https://github.com/MrThearMan/django-browsable-router)\n\n---\n',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrThearMan/django-browsable-router',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4',
}


setup(**setup_kwargs)
