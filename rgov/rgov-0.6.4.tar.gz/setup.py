# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rgov', 'rgov.commands']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=0.8.1,<0.9.0',
 'fake-useragent>=0.1.11,<0.2.0',
 'python-daemon>=2.3.0,<3.0.0']

entry_points = \
{'console_scripts': ['rgov = rgov.application:main']}

setup_kwargs = {
    'name': 'rgov',
    'version': '0.6.4',
    'description': 'Check if campgrounds have availability on Recreation.gov',
    'long_description': '\n\n# rgov - Recreation.gov Campground Checker\n\n[![img](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)\n\n`rgov` is a command line program to check for campground availability on Recreation.gov. It is intended to be easy to use, and provides an interactive mode for easily searching for and checking multiple campgrounds for availability at once. It can also be used as a unix daemon that sends push notifications to your phone or other device when available sites are found.  \n\n## Installation\n\nRequires: Python 3.6+\n\nFrom pypi:\n\n$ `pip install rgov`\n\nManually:\n\n$ `git clone https://github.com/jsbmg/rgov`\n\n$ `cd rgov`\n\n$ `pip install . pyproject.toml`\n\nIn order to receive notifications, you will need to make an account with Pushsafer and configure it for use with your phone or device of choice. \n\nhttps://www.pushsafer.com/\n\n## Quick Start\nThe easiest way to run rgov is with the `run` command. Use it to build a list of campgrounds, enter your dates of stay, and start checking for available sites:\n\n`$ rgov run` \n\nThe `search`, `check`, and `daemon` commands provide the same functionality as above but non-interactively.\n\nRun $ `rgov` to see a list of all commands, and $ `rgov help <command>` to see more information about each one. \n',
    'author': 'Jordan Sweet',
    'author_email': 'hello@jordandsweet.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
