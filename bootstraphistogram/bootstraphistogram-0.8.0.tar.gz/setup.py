# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bootstraphistogram']

package_data = \
{'': ['*']}

install_requires = \
['boost-histogram>=1.0.0', 'matplotlib>=3.1,<4.0', 'numpy>=1.19.0,<2.0.0']

setup_kwargs = {
    'name': 'bootstraphistogram',
    'version': '0.8.0',
    'description': 'Poisson bootstrap histogram.',
    'long_description': '# bootstraphistogram \n\n[![Github Build Status](https://img.shields.io/github/workflow/status/davehadley/bootstraphistogram/ci?label=Github%20Build)](https://github.com/davehadley/bootstraphistogram/actions?query=workflow%3Aci)\n[![Documentation Status](https://readthedocs.org/projects/bootstraphistogram/badge/?version=latest)](https://bootstraphistogram.readthedocs.io/en/latest/?badge=latest)\n[![PyPI](https://img.shields.io/pypi/v/bootstraphistogram)](https://pypi.org/project/bootstraphistogram/)\n[![License: MIT](https://img.shields.io/pypi/l/bootstraphistogram)](https://github.com/davehadley/bootstraphistogram/blob/master/LICENSE.txt)\n[![Last Commit](https://img.shields.io/github/last-commit/davehadley/bootstraphistogram/dev)](https://github.com/davehadley/bootstraphistogram)\n\nA python package that provides a multi-dimensional histogram with automatic Poisson bootstrap re-sampling.\n\n# Installation\n\nInstall with pip from PyPI:\n```bash\npython -m pip install bootstraphistogram\n```\n\n# Usage Instructions\n\nFor usage instructions and examples see the documentation at: <https://bootstraphistogram.readthedocs.io>.\n\n# Development Instructions\n\nFor Linux systems, the provided setup script will setup a suitable python virtual environment \nand install pre-commit-hooks.\n```bash\nsource setup.sh\n```\n\nThis package uses [Python poetry](https://python-poetry.org/) for dependency management.\n```bash\npoetry install\n```\n\nTo run the unit tests run:\n```bash\npoetry run pytest\n```\n\nTo build documentation run:\n```bash\npoetry run pip install sphinx && \\\npoetry run sphinx-build -W docs docs-build\n```\n\nTo auto-build the documentation while editing:\n```\npoetry run pip install sphinx-autobuild && sphinx-autobuild docs docs/_build/html \n```\nand find your documentation on <http://localhost:8000>.\n\nTo generate a test coverage report run:\n```bash\npoetry run coverage run -m pytest tests && poetry run coverage report -m\n```',
    'author': 'David Hadley',
    'author_email': 'davehadley@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/davehadley/bootstraphistogram',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
