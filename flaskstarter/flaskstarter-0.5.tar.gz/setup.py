# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flaskstarter', 'flaskstarter.tools']

package_data = \
{'': ['*'], 'flaskstarter': ['templates/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0', 'MarkupSafe>=2.0.1,<3.0.0', 'click>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['flaskstarter = flaskstarter.flaskstart_cli:flaskstarter']}

setup_kwargs = {
    'name': 'flaskstarter',
    'version': '0.5',
    'description': 'A Flask project start-up CLI to create Flask modular ready projects.',
    'long_description': "# flaskstarter\n\n![](https://img.shields.io/pypi/l/flaskstarter) ![](https://img.shields.io/pypi/v/flaskstarter) ![](https://img.shields.io/pypi/wheel/flaskstarter) \n\nA Flask project start-up CLI to create modular ready projects.\n\nFlaskstarter assumes you know about Flask microframework and its mechanics in a begginer level. It can be really helpful if you are still using monolithic aproach, and needs to start using a modular architecture.\n\nIt also assumes you are using Python 3.6+.\n\n> Flaskstarter recommends the use of a python virtual environment for project\n> to work safely and isolated from your systems binnaries. Activate it before\n> the next steps.\n\nTo install flaskstarter use the usual:\n\n`pip install flaskstarter`\n\nTo see its version:\n\n`flaskstarter --version`\n\nTo see its help:\n\n`flaskstarter --help`\n\nTo start a project, create its folder and:\n\n`flaskstarter init main_module_name`\n\nIf you do want to use the same project's root folder as main module name:\n\n`flaskstarter init .`\n\nTo see init's help:\n\n`flaskstarter init --help`\n\nNow, after project creation, you can  make full use of manage.py, a script\nwith a CLI that may help you to automate some tasks inside project tree.\n\nBy now you can create a blueprint structure by typing the bellow on project root:\n\n`$ python manage.py plug-blueprint [blueprint_name]`\n\nIf it will work as an API blueprint, that's enough. But maybe it is not and you want to use private templates related only to this blueprint. This is solved by adding a '-t' or '--templates' to the above command.\n\nAfter that, remember to go onto app init file to register the blueprint on it. There is an EXTENSIONS variable where you can list all the plugins to autoimport. It uses factory design.\n\nTo run your app you can use the bellow on project root:\n\n`$ python manage.py runserver`\n\nAsk manage.py for runserver help to see its options.\n\nNow it is possible to plug a database and a migration extensions to the project. For a first experience Flaskstarter is running with flask-sqlalchemy and flask-migrate. The templates that generate the kickoff database use sqlite and the simplest thing possible. You will be able to plug a database by running:\n\n`$ python manage.py plug-database`\n\nWhen plug-database is ran, the manage script will create the migrations folder as \nAlembic requires. Once it is created the following commands will be available.\n\nThis will generate a migration script with Example as message:\n\n`$ python manage.py db-migrate Example`\n\nThis upgrades the database:\n\n`$ python manage.py db-upgrade`\n\nIf anything undesirable happens, this will downgrade the database:\n\n`$ python manage.py db-downgrade`\n\nFor other Flask-Migrate commands, you can export FLASK_APP on your shell and use\nflask db (command) as its documentation guides.\n\n## What the project does for you\n\nIt creates project tree, a functional virtualenv on .venv, the init and routes files with a helloworld example and a manage.py script to run the project with the virtual enviroment created and attach blueprints to it. It now installs the requirements on project's .venv on POSIX systems. Feel free to change to poetry and pyproject.toml pattern.\n\nA word of warning: when commiting and pushing your project to versioning servers, remember to put instance folder into .gitignore, if not yet. And then remember to place it into deploy destination.\n\n## What the project does not do for you\n\nIt doesn't force you to use poetry or any other tool but flask, toml and dynaconf on the Flask project created.\n\n## Future\n\n- Add automated tests for development enviroment of flaskstarter\n- Work on a better architecture for the generated project\n- Start new extensions by manage.py creating an empty skeleton\n\n## How can you help on flaskstarter development?\n\nFeel free to clone it and send us pull requests! Remember to comment the decisions you make so they can be better reviewed.\n",
    'author': 'Felipe Bastos Nunes',
    'author_email': 'felipe.bastosn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/felipebastos/flaskstart',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
