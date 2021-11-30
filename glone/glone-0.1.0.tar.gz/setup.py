# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glone']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'fastcore>=1.3.27,<2.0.0',
 'ghapi>=0.1.19,<0.2.0',
 'humanize>=3.13.1,<4.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['glone = glone.cli:main']}

setup_kwargs = {
    'name': 'glone',
    'version': '0.1.0',
    'description': 'A Python CLI to backup all your GitHub repositories.',
    'long_description': '# glone\n\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA Python CLI to backup all your GitHub repositories.\n\n## Development\n\n- `poetry install`\n- `poetry shell`\n\n## Tech Stack\n\n- [Click](https://click.palletsprojects.com/) (for the interface)\n\n### Packaging and Development\n\n- [Poetry](https://python-poetry.org/)\n- [Mypy](http://mypy-lang.org/)\n- [isort](https://pycqa.github.io/isort/)\n- [Black](https://github.com/psf/black)\n- [Flake8](https://flake8.pycqa.org/)\n  - [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear)\n  - [flake8-comprehensions](https://github.com/adamchainz/flake8-comprehensions)\n  - [pep8-naming](https://github.com/PyCQA/pep8-naming)\n  - [flake8-builtins](https://github.com/gforcada/flake8-builtins)\n- [Bandit](https://bandit.readthedocs.io/)\n\nThis CLI was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`joaopalmeiro/cookiecutter-templates/python-cli`](https://github.com/joaopalmeiro/cookiecutter-templates) project template.\n\n## Notes\n\n- [Backup script](https://github.com/joaopalmeiro/scriptkit-playground/blob/main/google-zx/backup-gh.mjs).\n- [ghapi documentation](https://ghapi.fast.ai/) ([API](https://ghapi.fast.ai/fullapi.html)).\n- Commands:\n  - `glone joaopalmeiro`.\n  - `glone joaopalmeiro -o ~/Downloads`.\n  - `glone joaopalmeiro -o ~/Downloads -f tar`.\n  - `glone --help`.\n  - `glone --version`.\n- [GitPython](https://github.com/gitpython-developers/GitPython) package.\n- [GitHub CLI](https://cli.github.com/) (a.k.a. `gh`).\n- [humanize](https://github.com/jmoiron/humanize/) package. `poetry add humanize`.\n',
    'author': 'João Palmeiro',
    'author_email': 'joaommpalmeiro@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/joaopalmeiro/glone',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
