# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sttgeo']
setup_kwargs = {
    'name': 'sttgeo',
    'version': '1.0.0',
    'description': 'Information of IP.... For example: IP, TimeZone, Region, City, Country and soon...',
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
