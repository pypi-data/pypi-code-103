# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_pydocstyle']

package_data = \
{'': ['*']}

install_requires = \
['pydocstyle>=6.1.1,<7.0.0']

entry_points = \
{'flake8.extension': ['D = flake8_pydocstyle:Flake8PydocstylePlugin']}

setup_kwargs = {
    'name': 'flake8-pydocstyle',
    'version': '0.2.0',
    'description': 'flake8 plugin that integrates pydocstyle',
    'long_description': '[![license](https://img.shields.io/github/license/KRunchPL/flake8-pydocstyle.svg)](https://github.com/KRunchPL/flake8-pydocstyle/blob/master/LICENSE)\n\n[![latest release](https://img.shields.io/github/release/KRunchPL/flake8-pydocstyle.svg)](https://github.com/KRunchPL/flake8-pydocstyle/releases/latest) [![latest release date](https://img.shields.io/github/release-date/KRunchPL/flake8-pydocstyle.svg)](https://github.com/KRunchPL/flake8-pydocstyle/releases)\n\n[![PyPI version](https://img.shields.io/pypi/v/flake8-pydocstyle)](https://pypi.org/project/flake8-pydocstyle/) [![Python](https://img.shields.io/pypi/pyversions/flake8-pydocstyle)](https://pypi.org/project/flake8-pydocstyle/)\n\n# flake8-pydocstyle\n\nPlugin for [`flake8`](https://github.com/PyCQA/flake8) that runs [`pydocstyle`](https://github.com/PyCQA/pydocstyle/) while linting.\n\nIt is running `pydocstyle` as it would be run without any parameters in the command line, so it respects all configuration file options that you can set for example in `pyproject.toml`.\n\n## Reason\n\nMaybe you ask a question why just not use [`flake8-docstrings`](https://github.com/PyCQA/flake8-docstrings). In my use-case I wanted to keep the configuration in the `pyproject.toml` file and be able to use everything that `pydocstyle` has to offer in terms of customization. The `flake8-docstrings` is not reading the `pydocstyle` config files, but provides its own options which was insufficient to me.\n\n## Contributing\n\nIf you wish to contribute feel free to create an issue or just straight away fork and create PR to this repository. To save your and my time on discussions please provide a good description for them.\n\n## Development\n\nDevelopment documentation can be found [here](README-DEV.md)\n',
    'author': 'KRunchPL',
    'author_email': 'krunchfrompoland@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/KRunchPL/flake8-pydocstyle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
