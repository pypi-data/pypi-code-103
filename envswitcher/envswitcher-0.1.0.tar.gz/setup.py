# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['envswitcher']
install_requires = \
['typer[all]<0.4']

entry_points = \
{'console_scripts': ['es = envswitcher:app']}

setup_kwargs = {
    'name': 'envswitcher',
    'version': '0.1.0',
    'description': 'Switch between envfiles',
    'long_description': '# envswitcher\n',
    'author': 'Jack Reilly',
    'author_email': 'jackdreilly@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
