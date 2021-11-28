# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['board_game_recommender']

package_data = \
{'': ['*']}

install_requires = \
['pytility>=0.3.0,<0.4.0', 'turicreate>=6.4.1,<7.0.0']

setup_kwargs = {
    'name': 'board-game-recommender',
    'version': '2.1.5',
    'description': 'Board games recommender engine',
    'long_description': None,
    'author': 'Markus Shepherd',
    'author_email': 'markus@recommend.games',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
