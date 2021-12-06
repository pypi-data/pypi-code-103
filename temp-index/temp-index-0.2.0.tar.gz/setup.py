# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['temp_index']
install_requires = \
['calibrestekje>=0.0.3,<0.0.4', 'reportlab>=3.6.3,<4.0.0']

setup_kwargs = {
    'name': 'temp-index',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'automatist',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
