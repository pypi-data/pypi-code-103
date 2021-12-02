# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mdweek']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mdweek',
    'version': '1.2.0',
    'description': 'a utility package handling week based calculations',
    'long_description': None,
    'author': 'Yasunori Horikoshi',
    'author_email': 'hotoku@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
