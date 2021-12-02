# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['executor']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=3.0.0,<4.0.0',
 'connect-openapi-client>=24.0',
 'connect-reports-core>=23.0.0,<23.1.0',
 'lxml>=4.0.0,<5.0.0',
 'openpyxl>=3.0.0,<4.0.0',
 'requests>=2.0.0,<3.0.0']

entry_points = \
{'console_scripts': ['cextrun = executor.runner:run_executor']}

setup_kwargs = {
    'name': 'connect-reports-runner',
    'version': '24.2',
    'description': 'Connect Reports Runner',
    'long_description': 'Connect Reports Executor\n========================\n\nThis project contains the executor code used to run custom reports on CloudBlue Connect.\n',
    'author': 'CloudBlue',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://connect.cloudblue.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<3.9.0',
}


setup(**setup_kwargs)
