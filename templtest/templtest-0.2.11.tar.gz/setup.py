# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['templtest']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=20.9,<21.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['ansible-base>=2.10,<2.11'],
 ':python_version >= "3.7" and python_version < "3.8"': ['ansible-core>=2.11,<2.12'],
 ':python_version >= "3.8" and python_version < "4.0"': ['ansible-core>=2.12,<3.0']}

entry_points = \
{'console_scripts': ['templtest = templtest.cli:main']}

setup_kwargs = {
    'name': 'templtest',
    'version': '0.2.11',
    'description': 'A tool for testing Ansible role templates.',
    'long_description': None,
    'author': 'Alexey Busygin',
    'author_email': 'yaabusygin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
