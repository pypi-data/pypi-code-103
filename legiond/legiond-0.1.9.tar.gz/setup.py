# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['legiond']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'legion-utils>=0.2.3,<0.3.0',
 'pydantic>=1.7.3,<2.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'robotnikmq>=0.3.0,<0.4.0',
 'typeguard>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['legiond = legiond.cli:cli']}

setup_kwargs = {
    'name': 'legiond',
    'version': '0.1.9',
    'description': 'A distributed, scalable, and fault-tolerant alerting and monitoring system',
    'long_description': '# LegionD\n\nThe monitoring service daemon for Legion - a distributed, scalable, and fault-tolerant alerting and monitoring system\n\n## Setup & Usage\n\n### Installation\n\nTODO\n\n### Configuration\n\nTODO\n\n### Usage\n\nThe key reference for using `legiond` is:\n\n```bash\nlegiond --help\n```\n\n## Development\n\n### Standards\n\n- Be excellent to each other\n- Code coverage must be at 100% for all new code, or a good reason must be provided for why a given bit of code is not covered.\n  - Example of an acceptable reason: "There is a bug in the code coverage tool and it says its missing this, but its not".\n  - Example of unacceptable reason: "This is just exception handling, its too annoying to cover it".\n- The code must pass the following analytics tools. Similar exceptions are allowable as in rule 2.\n  - `pylint --disable=C0111,W1203,R0903 --max-line-length=100 ...`\n  - `flake8 --max-line-length=100 ...`\n  - `mypy --ignore-missing-imports --follow-imports=skip --strict-optional ...`\n- All incoming information from users, clients, and configurations should be validated.\n- All internal arguments passing should be typechecked whenever possible with `typeguard.typechecked`\n\n### Development Setup\n\nUsing [poetry](https://python-poetry.org/) install from inside the repo directory:\n\n```bash\npoetry install\n```\n\nThis will set up a virtualenv which you can always activate with either `poetry shell` or run specific commands with `poetry run`. All instructions below that are meant to be run in the virtualenv will be prefaced with `(legiond)$ `\n\n#### IDE Setup\n\n**Sublime Text 3**\n\n```bash\ncurl -sSL https://gitlab.com/-/snippets/2066312/raw/master/poetry.sublime-project.py | poetry run python\n```\n\n#### Development\n\n### Testing\n\nAll testing should be done with `pytest` which is installed with the `dev` requirements.\n\nTo run all the unit tests, execute the following from the repo directory:\n\n```bash\n(legiond)$  pytest\n```\n\nThis should produce a coverage report in `/path/to/dewey-api/htmlcov/`\n\nWhile developing, you can use [`watchexec`](https://github.com/watchexec/watchexec) to monitor the file system for changes and re-run the tests:\n\n```bash\n(legiond)$ watchexec -r -e py,yaml pytest\n```\n\nTo run a specific test file:\n\n```bash\n(legiond)$ pytest tests/unit/test_cli.py\n```\n\nTo run a specific test:\n\n```bash\n(legiond)$ pytest tests/unit/test_cli.py::test_cli_basics\n```\n\nFor more information on testing, see the `pytest.ini` file as well as the [documentation](https://docs.pytest.org/en/stable/).\n',
    'author': 'Eugene Kovalev',
    'author_email': 'eugene@kovalev.systems',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/legion-robotnik/legiond',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
