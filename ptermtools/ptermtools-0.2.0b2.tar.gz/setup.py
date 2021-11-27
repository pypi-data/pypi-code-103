# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ptermtools', 'ptermtools.git_repo_organizer', 'ptermtools.sus_files']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'click8>=8.0.1,<9.0.0',
 'docker>=5.0.3,<6.0.0',
 'everett>=2.0.1,<3.0.0',
 'fs>=2.4.14,<3.0.0',
 'mongoengine>=0.23.1,<0.24.0',
 'param>=1.12.0,<2.0.0',
 'pymongo>=3.12.1,<4.0.0',
 'python-gitlab>=2.10.1,<3.0.0',
 'spython>=0.1.17,<0.2.0',
 'taskw>=1.3.0,<2.0.0',
 'xdg>=5.1.1,<6.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.2,<5.0.0']}

entry_points = \
{'console_scripts': ['sus-files = ptermtools.sus_files.cli:main']}

setup_kwargs = {
    'name': 'ptermtools',
    'version': '0.2.0b2',
    'description': "Paul's Terminal Tools",
    'long_description': "[![PyPI Version](https://img.shields.io/pypi/v/ptermtools)](https://pypi.org/project/ptermtools/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/ptermtools)](https://pypi.org/project/ptermtools/)\n[![Python Wheel](https://img.shields.io/pypi/wheel/ptermtools)](https://pypi.org/project/ptermtools/)\n[![License](https://img.shields.io/badge/License-Apache2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Code Quality: flake8](https://img.shields.io/badge/code%20quality-flake8-000000.svg)](https://gitlab.com/pycqa/flake8)\n\n# ptermtools\nPaul's Terminal Tools\n\n## Contributing\nPlease refer to [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to\ncontribute to this project.\n",
    'author': 'Paul Gierz',
    'author_email': 'paulgierz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
