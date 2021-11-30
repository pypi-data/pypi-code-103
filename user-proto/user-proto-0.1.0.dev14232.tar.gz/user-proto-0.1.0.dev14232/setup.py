# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['user_proto']

package_data = \
{'': ['*']}

install_requires = \
['pivi>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'user-proto',
    'version': '0.1.0.dev14232',
    'description': 'user proto messages and proto client',
    'long_description': None,
    'author': 'Anonymous pivi generator',
    'author_email': 'gen@ivi.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
