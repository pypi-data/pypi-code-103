# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clickhouse_migrate']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.2,<4.0.0', 'asynch>=0.1.9', 'python-dotenv>=0.19.1,<0.20.0']

entry_points = \
{'console_scripts': ['chmigrate = clickhouse_migrate.runner:run']}

setup_kwargs = {
    'name': 'chmigrate',
    'version': '0.5.0',
    'description': 'Utilites make ClickHouse migration',
    'long_description': 'CHMigrate is utils make and manage ClickHouse migrations\n\n### Make migration\n```shell\nchmigrate make <name>\n```\n\n### Up migrations\n```shell\nchmigrate up [step]\n```\n\n### Down migrations\n```shell\nchmigrate down [step]\n```\n\n### Show migrations\n```shell\nchmigrate show\n```\n\n### Force marks as success last dirty migration\n```shell\nchmigrate force\n```\n\n### Force reset last dirty migration\n```shell\nchmigrate reset\n```\n\n\n\n',
    'author': 'Vadim Statishin',
    'author_email': 'statishin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
