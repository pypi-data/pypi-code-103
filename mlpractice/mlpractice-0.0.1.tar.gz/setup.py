# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlpractice',
 'mlpractice.linear_classifier',
 'mlpractice.rnn_torch',
 'mlpractice.tests',
 'mlpractice.tests.linear_classifier',
 'mlpractice.tests.rnn_torch']

package_data = \
{'': ['*'],
 'mlpractice': ['templates/linear_classifier/*', 'templates/rnn_torch/*']}

install_requires = \
['numpy>=1.21.4,<2.0.0', 'scipy>=1.7.2,<2.0.0', 'torch>=1.10.0,<2.0.0']

entry_points = \
{'console_scripts': ['mlpractice = mlpractice.cli:command_line']}

setup_kwargs = {
    'name': 'mlpractice',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'Vladislav Ushakov',
    'author_email': 'uvd2001@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
