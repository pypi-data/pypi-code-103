# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['souvenir']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24,<4.0.0', 'tabulate>=0.8.9,<0.9.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['sv = souvenir.__main__:sv']}

setup_kwargs = {
    'name': 'souvenir',
    'version': '0.1.0',
    'description': 'Little CLI program which helps creating and viewing flashcards',
    'long_description': '# Souvenir\n\n> Little CLI program which helps creating and viewing flashcards\n\n## Usage\n\n```sh\n$ sv new french\n```\n\n```sh\n$ sv add souvenir memory\n```\n\n```sh\n$ sv list\n+------------+----------+---------+--------+----------+\n| Question   | Answer   |   Views |   Hits |   Misses |\n|------------+----------+---------+--------+----------|\n| souvenir   | memory   |       0 |      0 |        0 |\n+------------+----------+---------+--------+----------+\n```\n\n```sh\n$ sv repeat --times 50\n... [ Interactive repeat session ] ...\n```\n',
    'author': 'Denis Gruzdev',
    'author_email': 'codingjerk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codingjerk/souvenir',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
