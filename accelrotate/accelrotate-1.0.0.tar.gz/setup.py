# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['accelrotate']
install_requires = \
['click>=8.0.0,<9.0.0']

entry_points = \
{'console_scripts': ['accelrotate = accelrotate:cli']}

setup_kwargs = {
    'name': 'accelrotate',
    'version': '1.0.0',
    'description': 'Rotate linux devices (screens, touchpads etc) based on accelerometer',
    'long_description': None,
    'author': 'granitosaurus',
    'author_email': 'bernardas.alisauskas@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
