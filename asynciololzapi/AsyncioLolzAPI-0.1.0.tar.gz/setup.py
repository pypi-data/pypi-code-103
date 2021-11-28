# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['asynciololzapi']
setup_kwargs = {
    'name': 'asynciololzapi',
    'version': '0.1.0',
    'description': 'Асинхронная версия модуля LolzAPI',
    'long_description': None,
    'author': 'Shemdy',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
