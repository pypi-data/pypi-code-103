# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbt',
 'pbt.console',
 'pbt.package',
 'pbt.package.manager',
 'pbt.package.registry',
 'pbt.vcs']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'lbry-rocksdb-optimized>=0.8.1,<0.9.0',
 'loguru>=0.5.3,<0.6.0',
 'networkx>=2.6.3,<3.0.0',
 'orjson>=3.6.3,<4.0.0',
 'poetry>=1.1.8,<2.0.0',
 'pytest-mock>=3.6.1,<4.0.0',
 'semver>=2.13.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'typing-extensions>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['pab = pbt.cli:cli', 'pbt = pbt.cli:cli']}

setup_kwargs = {
    'name': 'pab',
    'version': '2.0.1',
    'description': 'A build tool for multi-projects that leverages package registries (pypi, npmjs, etc.)',
    'long_description': '<h1 align="center">PBT</h1>\n\n<div align="center">\n<b>pbt</b> — a build tool for multi-projects that leverages package registries (pypi, npmjs, etc.).\n    \n![PyPI](https://img.shields.io/pypi/v/pbt)\n![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)\n[![GitHub Issues](https://img.shields.io/github/issues/binh-vu/pbt.svg)](https://github.com/binh-vu/pbt/issues)\n![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)\n[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n\n</div>\n\n## Introduction\n\nHaving all projects in the same repository make it much easier to develop, share, reuse, and refactor code. Building and publishing the projects should not be done manually because it is time-consuming and may be frustrated if the projects are depending on each other. pbt is a tool designed to help make the process easier and faster. It supports building, installing, and updating versions of your projects and their dependencies consistently. It also provides utility commands to help you work with your projects in multi-repositories as if you are working with a monorepo.\n\n## Installation\n\n```bash\npip install -U pab  # not pbt\n```\n\n## Usage\n\nNote: currently, **pbt** supports Python projects configured with Poetry (an awesome dependency management that you should consider using).\n\n1. **Installing, cleaning, updating and publishing your projects**\n\nAssuming that you organized your projects as different sub-folders, each has their own project configuration file. \nIn the root directory (containing your projects), you can run `install` to install a specific project\n\n```bash\npbt install -p <project> [-e] [-d] [-v]\n```\n',
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/binh-vu/pbt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
