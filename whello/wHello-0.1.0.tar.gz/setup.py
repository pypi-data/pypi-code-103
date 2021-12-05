# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whello']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'whello',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Wissem Mansouri',
    'author_email': 'wissem.mansouri.ing@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
