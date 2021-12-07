# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dapr_httpx']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.21.1,<0.22.0']

setup_kwargs = {
    'name': 'dapr-httpx',
    'version': '0.2.0',
    'description': '✨dapr ➕ ✨httpx is awesome',
    'long_description': None,
    'author': 'Ben',
    'author_email': 'moon791017@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
