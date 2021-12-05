# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['tele_muninn']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv', 'python-telegram-bot', 'requests']

entry_points = \
{'console_scripts': ['tele-muninn = tele_muninn.console:cli']}

setup_kwargs = {
    'name': 'tele-muninn',
    'version': '0.0.3',
    'description': 'Just like Alfred but for Telegram',
    'long_description': "# tele-muninn\n\n[![PyPI](https://img.shields.io/pypi/v/tele-muninn?style=flat-square)](https://pypi.python.org/pypi/tele-muninn/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tele-muninn?style=flat-square)](https://pypi.python.org/pypi/tele-muninn/)\n[![PyPI - License](https://img.shields.io/pypi/l/tele-muninn?style=flat-square)](https://pypi.python.org/pypi/tele-muninn/)\n[![Coookiecutter - Wolt](https://img.shields.io/badge/cookiecutter-Wolt-00c2e8?style=flat-square&logo=cookiecutter&logoColor=D4AA00&link=https://github.com/woltapp/wolt-python-package-cookiecutter)](https://github.com/woltapp/wolt-python-package-cookiecutter)\n\n\n---\n\n**Documentation**: [https://namuan.github.io/tele-muninn](https://namuan.github.io/tele-muninn)\n\n**Source Code**: [https://github.com/namuan/tele-muninn](https://github.com/namuan/tele-muninn)\n\n**PyPI**: [https://pypi.org/project/tele-muninn/](https://pypi.org/project/tele-muninn/)\n\n---\n\nJust like Alfred but for Telegram\n\n## Installation\n\n```sh\npip install tele-muninn\n```\n\n## Usage\n\nSetup following environment variables:\n```\nexport TELE_MUNINN_BOT_TOKEN=\n```\n\nRun following command:\n```\ntele-muninn\n```\n\n## Development\n\n* Clone this repository\n* Requirements:\n  * [Poetry](https://python-poetry.org/)\n  * Python 3.7+\n* Create a virtual environment and install the dependencies\n\n```sh\npoetry install\n```\n\n* Activate the virtual environment\n\n```sh\npoetry shell\n```\n\n### Testing\n\n```sh\npytest\n```\n\n### Releasing\n\nTrigger the [Draft release workflow](https://github.com/namuan/tele-muninn/actions/workflows/draft_release.yml)\n(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.\n\nFind the draft release from the\n[GitHub releases](https://github.com/namuan/tele-muninn/releases) and publish it. When\n a release is published, it'll trigger [release](https://github.com/namuan/tele-muninn/blob/master/.github/workflows/release.yml) workflow which creates PyPI\n release and deploys updated documentation.\n\n### Makefile\n\nRun `make` to see the list of available commands.\n",
    'author': 'Namuan',
    'author_email': 'github@deskriders.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://namuan.github.io/tele-muninn',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
