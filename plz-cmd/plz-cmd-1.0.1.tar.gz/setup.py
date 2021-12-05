# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['plz']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=3.0', 'colorama>=0.4,<0.5']

extras_require = \
{':python_version >= "3.5" and python_version < "4.0"': ['jsonschema>=3.2.0,<4.0.0'],
 ':python_version >= "3.7"': ['jsonschema>=4.2.0,<5.0.0']}

entry_points = \
{'console_scripts': ['plz = plz.main:main']}

setup_kwargs = {
    'name': 'plz-cmd',
    'version': '1.0.1',
    'description': 'command line app for running configurable shell commands',
    'long_description': "## plz-cmd\n\n[![Build Status](https://travis-ci.org/m3brown/plz.svg?branch=master)](https://travis-ci.org/m3brown/plz)\n[![Coverage Status](https://coveralls.io/repos/github/m3brown/plz/badge.svg?branch=master)](https://coveralls.io/github/m3brown/plz?branch=master)\n\nA shell command to execute standard/repeatable commands in a git repo\n\n### Installation\n\nInstall plz at the system level so that it only has to be installed once.\n\n```bash\npip install plz-cmd\n\n# sudo may be required on your machine\nsudo pip install plz-cmd\n```\n\nIt can also be installed inside a virtualenv.  However, this means you'll have\nto install plz-cmd for each each virtualenv in use.\n\n```bash\nvirtualenv venv\n. venv/bin/activate\n\npip install plz-cmd\n```\n\n### Example\n\nplz looks for a `plz.yaml` file either in the current directory or in the root\nof the git repo you're currently in. This file can (and should) be checked into\nversion control.\n\nFor a plz.yaml file located in the git root directory, commands run will be\nexecuted relative to that directory, not the current directory.\n\nSuppose we have the following `plz.yaml` file:\n\n```yaml\ncommands:\n  run:\n    cmd: ./manage.py runserver\n  test:\n    cmd:\n    - ./manage.py test\n    - yarn test\n  setup:\n    cmd:\n    - poetry install\n    - poetry run ./manage.py migrate\n    - yarn install\n  ls:\n    cmd: ls\n```\n\nThe following commands would be available:\n\n```bash\nplz run\nplz test\nplz setup\n```\n\n### Getting help\n\nList all the available commands with:\n\n```bash\nplz\n# or\nplz help\n```\n\nPrint the yaml schema for any defined command with `plz help <command>`:\n\n```\n> plz help test\n[INFO] Using config: plz.yaml\n\ntest:\n  cmd:\n  - poetry run python -m pytest\n```\n\n### Environment variables\n\nEnvironment variables can be set for an individual command or globally for all commands.\n\n```yaml\n# env variable for an individual command\ncommands:\n  run:\n    cmd: ./manage.py runserver\n  test:\n    cmd: ./manage.py test\n    env:\n      DJANGO_SETTINGS_MODULE: myapp.settings.test\n```\n\n```yaml\nglobal_env:\n  ACCESS_TOKEN: 12345\ncommands:\n  run:\n    cmd: ./manage.py runserver\n```\n\n### Globbing\n\nplz supports asterisk expansion.  For example, the cmd `ls *.py` will work as expected.\n\n### Runtime arguments\n\nplz supports passing custom arguments when running the plz command. For example:\n\n```\n# bind to port 8001 instead of the default 8000\nplz run 127.0.0.1:8001\n```\n\nAny passed arguments will be tested to see if they are file paths relative to\nthe current directory when running the command. Using this repo as an example:\n\n```\nbash$ ls .*.yaml\nplz.yaml               .pre-commit-config.yaml\n\nbash$ cd plz\n\nbash$ plz ls ../.*.yaml\n\n[INFO] Using config: /path/plz/plz.yaml\n\n===============================================================================\nRunning command: ls\n===============================================================================\n\nplz.yaml\n.pre-commit-config.yaml\n\n[INFO] Process complete, return code: 0\n\nbash$ plz ls __*.py\n\n[INFO] Using config: /path/plz/plz.yaml\n\n===============================================================================\nRunning command: ls\n===============================================================================\n\nplz/__init__.py\n\n[INFO] Process complete, return code: 0\n```\n\n### Development\n\nSetting up for development is easy when plz is already installed!\n\n```\ngit clone https://github.com/m3brown/plz\ncd plz\nplz setup\nplz test\n```\n",
    'author': 'Mike Brown',
    'author_email': 'mike.brown@excella.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m3brown/plz',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
