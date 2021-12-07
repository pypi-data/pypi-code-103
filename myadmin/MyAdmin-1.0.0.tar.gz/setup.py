# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['myadmin']
setup_kwargs = {
    'name': 'myadmin',
    'version': '1.0.0',
    'description': 'Make a PowerShell console in your python code. (With password.) Password: "223345"',
    'long_description': None,
    'author': 'OwoNicoo',
    'author_email': '86409467+DiscordBotML@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
