# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['minecraft_server_updater']
install_requires = \
['beautifulsoup4>=4.8.2,<5.0.0',
 'click-spinner>=0.1.8,<0.2.0',
 'click>=7.0,<8.0',
 'click_log>=0.3.2,<0.4.0',
 'requests>=2.22,<3.0']

entry_points = \
{'console_scripts': ['msu = minecraft_server_updater:main']}

setup_kwargs = {
    'name': 'minecraft-server-updater',
    'version': '0.1.0',
    'description': 'pull down most recent server jar file (for Java edition)',
    'long_description': None,
    'author': 'Ryan',
    'author_email': 'citizen.townshend@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
