# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['balder',
 'balder.fields',
 'balder.filters',
 'balder.types',
 'balder.types.mutation',
 'balder.types.query',
 'balder.types.subscription']

package_data = \
{'': ['*'], 'balder': ['.vscode/*', 'templates/balder/*']}

install_requires = \
['Django>=3.1,<4.0',
 'django-filter>=2.4.0,<3.0.0',
 'graphene-django>=2.15.0,<3.0.0',
 'graphene-file-upload>=1.3.0,<2.0.0']

extras_require = \
{'subscription': ['channels>=3.0.3,<4.0.0',
                  'django-channels-graphql-ws>=0.8.0,<0.9.0']}

setup_kwargs = {
    'name': 'balder',
    'version': '0.1.15',
    'description': '',
    'long_description': None,
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
