# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['game', 'game.image', 'game.level', 'game.sound']

package_data = \
{'': ['*']}

install_requires = \
['urllib3>=1.26.7,<2.0.0']

setup_kwargs = {
    'name': 'mpl-talk',
    'version': '0.1.0',
    'description': 'A library example for Modules, Packages and Libaries talk',
    'long_description': '# mpl-talk\n\nThis is a library example for Modules, Packages and Libraries talk.\n',
    'author': 'Cristian Vera',
    'author_email': 'cristian.vera@mercadolibre.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
