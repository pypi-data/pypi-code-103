# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hugtools', 'hugtools.jupyter', 'hugtools.nlp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hugtools',
    'version': '0.1.0a3',
    'description': 'Some common tools that I have written over time',
    'long_description': None,
    'author': 'Adam Huganir',
    'author_email': 'adam@huganir.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adam-huganir/hugtools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
