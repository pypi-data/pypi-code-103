# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ubconvert']
setup_kwargs = {
    'name': 'ubconvert',
    'version': '1.22',
    'description': 'Time, Temperature, Speed, Distance, Volume, Weight conversion module',
    'long_description': None,
    'author': 'ZennDogg, Utility_Belt Designs, Tacoma, WA',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
