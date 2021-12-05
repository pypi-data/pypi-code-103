# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgmerge', 'pgmerge.tests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<6.1',
 'SQLAlchemy>=1.4.27,<2.0.0',
 'appdirs>=1.4.4,<1.5.0',
 'networkx==2.5',
 'psycopg2-binary',
 'rxjson==0.3',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['pgmerge = pgmerge.pgmerge:cli_app']}

setup_kwargs = {
    'name': 'pgmerge',
    'version': '1.9.0',
    'description': 'PostgreSQL data import/export utility',
    'long_description': "# pgmerge - a PostgreSQL data import and merge utility\n\n[![Build Status](https://github.com/samuller/pgmerge/workflows/tests/badge.svg)](https://github.com/samuller/pgmerge/actions)\n[![PyPI Version](https://badge.fury.io/py/pgmerge.svg)](https://badge.fury.io/py/pgmerge)\n[![Code Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/samuller/3c84321138784d39b31a02d7fe93b31d/raw/badge-coverage.json)](https://github.com/samuller/pgmerge/actions)\n\nThis utility's main purpose is to manage a set of CSV files that correspond with tables in a PostgreSQL database. Each of these CSV files can then be *merged* into their table, meaning that the following process will occur (also called an *upsert* operation):\n\n* Rows whose primary key don't yet exist in the table will be imported.\n* When the primary key already exists, row values will be updated.\n* Rows that are missing or unchanged will be ignored.\n\npgmerge can then also export data in the *same format* expected for import.\n\nThese features allow you to move data between databases with the same schema to keep them up to date and in sync, although it does not cover handling deleted data.\n\n    $ pgmerge --help\n    Usage: pgmerge [OPTIONS] COMMAND [ARGS]...\n\n    Merges data in CSV files into a Postgresql database.\n\n    Options:\n    --version  Show the version and exit.\n    --help     Show this message and exit.\n\n    Commands:\n    export  Export each table to a CSV file.\n    import  Import/merge each CSV file into a table.\n    inspect  Inspect database schema in various ways.\n\n### Import\n\n    $ pgmerge import --help\n    Usage: pgmerge import [OPTIONS] DIRECTORY [TABLES]...\n\n    Import/merge each CSV file into a table.\n\n    All CSV files need the same name as their matching table and have to be located\n    in the given directory. If one or more tables are specified then only they will\n    be used, otherwise all tables found will be selected.\n\n    Options:\n    -d, --dbname TEXT               Database name to connect to.  [required]\n    -h, --host TEXT                 Database server host or socket directory.\n                                    [default: localhost]\n    -p, --port TEXT                 Database server port.  [default: 5432]\n    -U, --username TEXT             Database user name.  [default: postgres]\n    -s, --schema TEXT               Database schema to use.  [default: public]\n    -w, --no-password               Never prompt for password (e.g. peer\n                                    authentication).\n    -W, --password TEXT             Database password (default is to prompt for\n                                    password or read config).\n    -L, --uri TEXT                  Connection URI can be used instead of specifying\n                                    parameters separately (also sets --no-password).\n    -f, --ignore-cycles             Don't stop import when cycles are detected in\n                                    schema (will still fail if there are cycles in\n                                    data)\n    -F, --disable-foreign-keys      Disable foreign key constraint checking during\n                                    import (necessary if you have cycles, but requires\n                                    superuser rights).\n    -c, --config PATH               Config file for customizing how tables are\n                                    imported/exported.\n    -i, --include-dependent-tables  When selecting specific tables, also include all\n                                    tables on which they depend due to foreign key\n                                    constraints.\n    --help                          Show this message and exit.\n\n## Installation\n\n> WARNING: the reliability of this utility is not guaranteed and loss or corruption of data is always a possibility.\n\n### Install from PyPI\n\nWith `Python 3` installed on your system, you can run:\n\n    pip install pgmerge\n\n(your `pip --version` has to be 9.0 or greater). To test that installation worked, run:\n\n    pgmerge --help\n\nand you can uninstall at any time with:\n\n    pip uninstall pgmerge\n\n### Install from Github\n\nTo install the newest code directly from Github:\n\n    pip install git+https://github.com/samuller/pgmerge\n\n### Issues\n\nIf you have trouble installing and you're running a Debian-based Linux that uses `Python 2` as its system default, then you might need to run:\n\n    sudo apt install libpq-dev python3-pip python3-setuptools\n    sudo -H pip3 install pgmerge\n",
    'author': 'Simon Muller',
    'author_email': 'samullers@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samuller/pgmerge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
