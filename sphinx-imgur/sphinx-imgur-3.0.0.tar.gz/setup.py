# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_imgur']

package_data = \
{'': ['*']}

install_requires = \
['sphinx']

extras_require = \
{':extra == "docs"': ['sphinxext-opengraph'],
 'docs': ['sphinx-copybutton',
          'sphinx-notfound-page',
          'sphinx-panels',
          'sphinx-rtd-theme',
          'toml']}

setup_kwargs = {
    'name': 'sphinx-imgur',
    'version': '3.0.0',
    'description': 'Embed Imgur images and albums in Sphinx documents/pages.',
    'long_description': '# sphinx-imgur\n\nEmbed [Imgur](https://imgur.com) images and albums in Sphinx documents/pages.\n\n* Python 3.6, 3.7, 3.8, and 3.9 supported on Linux, macOS, and Windows.\n\n📖 Full documentation: https://sphinx-imgur.readthedocs.io\n\n[![Github-CI][github-ci]][github-link]\n[![Coverage Status][codecov-badge]][codecov-link]\n[![Documentation Status][rtd-badge]][rtd-link]\n[![Code style: black][black-badge]][black-link]\n[![PyPI][pypi-badge]][pypi-link]\n[![PyPI Downloads][pypi-dl-badge]][pypi-dl-link]\n\n[github-ci]: https://github.com/Robpol86/sphinx-imgur/actions/workflows/ci.yml/badge.svg?branch=main\n[github-link]: https://github.com/Robpol86/sphinx-imgur/actions/workflows/ci.yml\n[codecov-badge]: https://codecov.io/gh/Robpol86/sphinx-imgur/branch/main/graph/badge.svg\n[codecov-link]: https://codecov.io/gh/Robpol86/sphinx-imgur\n[rtd-badge]: https://readthedocs.org/projects/sphinx-imgur/badge/?version=latest\n[rtd-link]: https://sphinx-imgur.readthedocs.io/en/latest/?badge=latest\n[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black-link]: https://github.com/ambv/black\n[pypi-badge]: https://img.shields.io/pypi/v/sphinx-imgur.svg\n[pypi-link]: https://pypi.org/project/sphinx-imgur\n[pypi-dl-badge]: https://img.shields.io/pypi/dw/sphinx-imgur?label=pypi%20downloads\n[pypi-dl-link]: https://pypistats.org/packages/sphinx-imgur\n\n## Quickstart\n\nTo install run the following:\n\n```bash\npip install sphinx-imgur\n```\n\nTo use in Sphinx simply add to your `conf.py`:\n\n```python\nextensions = ["sphinx_imgur.imgur"]\n```\n\nAnd in your Sphinx documents:\n\n```rst\n.. imgur:: 611EovQ\n```\n\nOr to use Imgur\'s embed feature with an album:\n\n```rst\n.. imgur-embed:: a/9YZHA\n```\n',
    'author': 'Robpol86',
    'author_email': 'robpol86@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
