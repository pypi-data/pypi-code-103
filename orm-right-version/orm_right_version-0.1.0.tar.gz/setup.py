# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['orm_right_version']
install_requires = \
['black>=21.11b1,<22.0']

setup_kwargs = {
    'name': 'orm-right-version',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'TheBatya3',
    'author_email': '86134076+TheBatya3@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
