# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sttcv']
setup_kwargs = {
    'name': 'sttcv',
    'version': '1.0.0',
    'description': 'Convert("filename.txt").say()',
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
