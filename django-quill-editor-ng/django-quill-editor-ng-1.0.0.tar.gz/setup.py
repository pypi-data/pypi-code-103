# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_quill']

package_data = \
{'': ['*'],
 'django_quill': ['static/django_quill/*', 'templates/django_quill/*']}

install_requires = \
['django>=3,<4']

setup_kwargs = {
    'name': 'django-quill-editor-ng',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': '이한영',
    'author_email': 'dev@lhy.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.6,<4',
}


setup(**setup_kwargs)
