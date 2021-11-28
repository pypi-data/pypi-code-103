# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['main']
setup_kwargs = {
    'name': 'md5-brute-force',
    'version': '0.2.0',
    'description': 'Python script for brute forcing an md5 hash.',
    'long_description': None,
    'author': 'Vsevolod Mineev',
    'author_email': 'vsevolod.mineev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
