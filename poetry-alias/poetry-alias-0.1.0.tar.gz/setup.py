# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_alias', 'poetry_alias.tests']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0a2,<2.0.0', 'tomlkit>=0.7.2,<0.8.0']

entry_points = \
{'poetry.application.plugin': ['alias = poetry_alias:AliasPlugin']}

setup_kwargs = {
    'name': 'poetry-alias',
    'version': '0.1.0',
    'description': 'Pew-style project management for Poetry',
    'long_description': 'poetry-alias\n============\n\n[Pew][]-style project management for [Poetry][]\xa01.2 and higher.\n\npoetry-alias introduces a new `alias` command suite for Poetry which allows\nyou to define short names (“aliases”) for you Poetry-based projects, and then\nuse these to switch to the project directories from wherever you are.\n\n    $ cd $HOME/src/myproject\n    [~/src/myproject]$ poetry alias add myproject\n    [~/src/myproject]$ cd\n    $ poetry alias go myproject\n    Spawning shell within /home/user/.cache/pypoetry/virtualenvs/myproject-Hyrvhkrx-py3.8\n    [~/src/myproject]$ . /home/user/.cache/pypoetry/virtualenvs/myproject-Hyrvhkrx-py3.8/bin/activate\n    [~/src/myproject]$\n\n[Pew]: https://github.com/berdario/pew\n[Poetry]: https://python-poetry.org/\n\n\nInstallation\n------------\n\nInstall poetry-alias by running:\n\n    poetry plugin add poetry-alias\n\n\nCommands\n--------\n\n  * `poetry alias add eggs` — define “eggs” as alias for the current project.\n    If a different project already used “eggs” as its alias, the command would\n    abort with a corresponding error message.  Multiple aliases can be defined\n    per project.\n\n  * `poetry alias show` — show all aliases for the current project.\n\n  * `poetry alias list` — list all project aliases in alphabetical order along\n    with their assigned project directories.\n\n  * `poetry alias go eggs` — change to the directory of the project aliased\n    “eggs”, and activate the virtualenv.\n\n  * `poetry alias rm eggs` — remove the “eggs” project alias.  The alias name\n    is optional for this command; if omitted, the current projects’ aliases\n    will be removed.\n\n  * `poetry alias prune` — remove all aliases that no longer point to a\n    project directory.\n\n  * `poetry alias clean` — remove all alias definitions.\n\n\nContribute\n----------\n\n  * Issue Tracker: https://gitlab.com/obda/poetry-alias/-/issues\n  * Source Code: https://gitlab.com/obda/poetry-alias\n\n\nLicense\n-------\n\nThe project is licensed under the MIT license.\n',
    'author': 'Clemens Kaposi',
    'author_email': 'clemens.kaposi@obda.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
