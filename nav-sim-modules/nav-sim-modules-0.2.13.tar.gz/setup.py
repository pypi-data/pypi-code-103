# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nav_sim_modules',
 'nav_sim_modules.actioner',
 'nav_sim_modules.actioner.hueristic_autonomous_actioner',
 'nav_sim_modules.nav_components',
 'nav_sim_modules.scener',
 'nav_sim_modules.scener.chest_search_room']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'cython>=0.29.24,<0.30.0',
 'numpy>=1.20,<2.0',
 'randoor>=0.1.4.4,<0.2.0.0']

setup_kwargs = {
    'name': 'nav-sim-modules',
    'version': '0.2.13',
    'description': 'Components for software to simulate the environment of robot that use autonomous movement system such as ROS Navigation Stack.',
    'long_description': None,
    'author': 'Reona Sato',
    'author_email': 'www.shinderu.www@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wwwshwww/nav-sim-modules',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
