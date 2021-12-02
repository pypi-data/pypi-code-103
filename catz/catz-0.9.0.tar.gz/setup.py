# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['catz']

package_data = \
{'': ['*']}

install_requires = \
['click-default-group>=1.2.2,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'rich>=10.14.0,<11.0.0']

entry_points = \
{'console_scripts': ['catz = catz.app:main', 'test = tests.harness:run']}

setup_kwargs = {
    'name': 'catz',
    'version': '0.9.0',
    'description': 'A colourful syntax highlighting tool for your terminal',
    'long_description': None,
    'author': 'Craig Gumbley',
    'author_email': 'craiggumbley@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
