# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opendiamond', 'opendiamond.scope']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'cryptography>=35.0.0,<36.0.0', 'python-dateutil>=1.5']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.1,<5.0.0']}

entry_points = \
{'console_scripts': ['cookiecutter = opendiamond.scope.cli_generate:generate',
                     'diamond-newscope = opendiamond.scope.cli_import:import_',
                     'opendiamond-scope = opendiamond.scope.cli:cli'],
 'opendiamond.cli_plugins': ['scope = opendiamond.scope.cli:cli']}

setup_kwargs = {
    'name': 'opendiamond-scope',
    'version': '10.2.1',
    'description': 'OpenDiamond scope manipulation library and tools',
    'long_description': '# OpenDiamond-scope\n\nLibrary and tools for manipulating OpenDiamond search scopes.\n\n\n# To install the latest release from PyPI\n\n    pipx install opendiamond-scope          # or\n    pip install --user opendiamond-scope\n\n\n# Building from source\n\nFor development, a consistent development environment is managed with poetry.\nIf you are developing locally it is recommended to set up pre-commit git hooks.\n\n    poetry install\n    poetry run pre-commit install   # optional\n\nThe code can then be run from the managed environment.\n\n    poetry run opendiamond-scope -h\n\nRunning of tests and release tagging is done with nox, which should already be\ninstalled in the development environment at this point.\n\n    # run tests against different installed python interpreters\n    poetry run nox\n\n    # release version tagging (and publishing) are handled by a nox script\n    poetry run nox -s release -- [major/minor/patch]\n',
    'author': 'Carnegie Mellon University',
    'author_email': 'diamond@cs.cmu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://diamond.cs.cmu.edu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
