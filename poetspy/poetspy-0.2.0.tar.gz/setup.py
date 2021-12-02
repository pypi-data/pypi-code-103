# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetspy']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0,<9.0.0',
 'loguru>=0.5.3,<0.6.0',
 'marko>=1.0.1,<2.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['pt = poetspy.poets:main', 'ptg = poetspy.generate:main']}

setup_kwargs = {
    'name': 'poetspy',
    'version': '0.2.0',
    'description': 'A small cli util to show project directories',
    'long_description': "# Poets\n\n[![License](https://img.shields.io/github/license/jokeneversoke/poets)](https://github.com/JokeNeverSoke/poets/blob/master/LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/poetspy)](https://pypi.org/project/poetspy/)\n[![Build Status](https://travis-ci.com/JokeNeverSoke/poets.svg?branch=master)](https://travis-ci.com/JokeNeverSoke/poets)\n[![Coverage Status](https://coveralls.io/repos/github/JokeNeverSoke/poets/badge.svg?branch=master)](https://coveralls.io/github/JokeNeverSoke/poets?branch=master)\n[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/PyPI/poetspy)](https://libraries.io/pypi/poetspy)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/poetspy)](https://pypi.org/project/poetspy/)\n\nA small script that goes over the directories of the current directories, and print them\n`ls`-like, but also showing descriptions scraped to the best of the script's abilities\n\n![demonstration](https://raw.githubusercontent.com/JokeNeverSoke/poets/master/assets/demonstration.gif)\n\n\n## Getting Started\n\nInstallation with pip\n\n```bash\n$ pip install poetspy\n```\n\nInstallation with pipx\n\n```bash\n$ pipx install poetspy\n```\n\n## Usage\n\n### Basic\n\n```bash\n$ cd projects  # cd into my main project dir\n$ pt  # show my projects w/ descriptions\ndeno/\nstudy/ study - This project was bootstrapped with Create React App.\nhanasu/ hanasu\nipfs/\nrandomcodes/ randomcodes - Some personal random codes\nsusume/ susume - This template should help get you started developing with Vue 3 and Typescript in ...\nhns/ hns - UsageCommands\nstudy-backend/ node-js-getting-started - A sample Node.js app using Express\nBVG/ bvg - Generates a bad video from a noun and a verb\nlogic/ logic\npoetspy/ poetspy - A small cli util to show project directories\nrandomlogging/ My logging xps - blah blah blah, no one wants to write READMEs\nblog/ jokens-blog - A starter for a blog powered by Gatsby and Markdown\ncall/\nitermtests/\nworkflow/\njns/ jns - Some random css\nhtmldesktop/\nmodules/\nvapi/ tmp - yarn install\n```\n\n### Custom Title & Descriptions\n\n```bash\n$ cd project/\n$ ptg title Hello World Project  # set cwd title\ntitle set to Hello World Project\n$ ptg des Python Tutorial  # set cwd description\ndescription set to Python Tutoria\n```\n",
    'author': 'JokeNeverSoke',
    'author_email': 'zengjoseph@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jokeneversoke/poets',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
