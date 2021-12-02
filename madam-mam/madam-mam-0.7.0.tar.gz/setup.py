# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['madam',
 'madam.adapters',
 'madam.adapters.agents',
 'madam.adapters.bpmn',
 'madam.adapters.interfaces',
 'madam.adapters.process',
 'madam.adapters.repository',
 'madam.domains',
 'madam.domains.entities',
 'madam.domains.interfaces',
 'madam.domains.interfaces.process',
 'madam.domains.interfaces.repository',
 'madam.libs',
 'madam.slots',
 'madam.slots.graphql']

package_data = \
{'': ['*'],
 'madam.adapters.bpmn': ['assets/*'],
 'madam.adapters.repository': ['assets/migrations/*'],
 'madam.slots.graphql': ['assets/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'PyYAML==5.1.2',
 'adhesive-zeebe>=2021.4.3,<2022.0.0',
 'ariadne>=0.13.0,<0.14.0',
 'docker>=5.0.0,<6.0.0',
 'lxml>=4.6.3,<5.0.0',
 'psycopg2-binary>=2.8.6,<3.0.0',
 'python-sql>=1.2.2,<2.0.0',
 'rich>=10.2.2,<11.0.0',
 'timecode>=1.3.1,<2.0.0',
 'uvicorn>=0.14.0,<0.15.0',
 'watchgod>=0.7,<0.8',
 'yoyo-migrations>=7.3.2,<8.0.0']

entry_points = \
{'console_scripts': ['madam = madam.slots.cli:cli']}

setup_kwargs = {
    'name': 'madam-mam',
    'version': '0.7.0',
    'description': 'MADAM (TM) Multi Agent Digital Asset Manager - a MAM server for Docker Swarm to handle higly distributed media processes',
    'long_description': '# MADAM\n\nMADAM is the Multi Agent Digital Asset Manager.\n\nIt provides a three-tier architecture platform to handle workflow processing in a distributed environment.\n\nIt uses Docker swarm to dispatch processes in a cluster of machines.\n\nIt is a free (as freedom) software written in Python.\n\n## Documentation\n\n[Link to the documentation](https://m5231.gitlab.io/documentation/)\n\n## Support\n\nIf you find this project useful and want to contribute, please submit issues, merge requests. If you use it regularly,\nyou can help by the author by a financial support.\n\n<script src="https://liberapay.com/vit/widgets/button.js"></script>\n<noscript><a href="https://liberapay.com/vit/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a></noscript>\n\n## Requirements\n\nYou will need [Camunda Modeler 4.11+](https://github.com/camunda/camunda-modeler/releases) to easily create\nZeebe BPMN XML workflows for MADAM.\n\n## Licensing\n\nMADAM is licensed under the [Gnu Public License Version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).\n\nCamunda Modeler is licensed under [the MIT License (MIT)](https://mit-license.org/).\n\nAt its core, MADAM use [adhesive-zebe](https://github.com/vtexier/adhesive), a BPMN workflow python engine able to\nexecute Zeebe BPMN XML workflows. It is a fork of [adhesive](https://github.com/germaniumhq/adhesive) under\nthe original adhesive license that is [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)\n\n## System environment setup\n\n1. [Install Docker](https://docs.docker.com/engine/install/).\n\n2. [Configure userns-remap](https://docs.docker.com/engine/security/userns-remap/) to map container user `root` to a\n   host non-root user.\n\n3. Configure the dev station as a [Docker Swarm Manager](https://docs.docker.com/engine/swarm/).\n\n4. Install a [Postgresql](https://www.postgresql.org/download/) database server.\n   \n_You can use the Ansible playbook provided to install PostgreSQL locally with Docker,\nafter configuring `hosts.yaml`:_\n\n    make environment\n\n### Python environment setup\n\n* It requires Python 3.8+.\n\n* [Pyenv](https://github.com/pyenv/pyenv) should be used to choose the right version of Python, without breaking the\n  default Python of the Operating System.\n\n* A Python virtual environment should be created in a `.venv` folder.\n\n```bash\n    pyenv install 3.8.0\n    pyenv shell 3.8.0\n    python -m venv .venv \n    source .venv/bin/activate`\n```\n\n### Installation/Update\n\nFrom PyPI:\n\nIn a Python virtualenv:\n\n    pip install -U madam-mam\n\nIn your user install directory:\n\n    pip install --user -U madam-mam\n\nYou should have a the `madam` cli command available:\n\n    madam\n\nor\n\n    madam --help\n\nwill display command usage.\n\nTo have bash completion, you can type:\n\n    _MADAM_COMPLETE=source_bash madam > madam-complete.sh\n    sudo cp madam-complete.sh /etc/bash_completion.d/.\n\nFor another shell, replace `source_bash` by `source_zsh` or `source_fish`\n\n### Development environment\n\nInstall [Poetry](https://python-poetry.org/) with the custom installer:\n\n    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python\n\nInstall Python dependencies:\n\n    poetry install --no-root\n\nYou can use the madam-cli dev command:\n\n    ./bin/madam-cli\n\nGet `bin/madam-cli` bash shell completion:\n\n    _MADAM_CLI_COMPLETE=source_bash bin/madam-cli > madam-cli-complete.sh\n    sudo cp madam-cli-complete.sh /etc/bash_completion.d/.\n\nFor another shell, replace `source_bash` by `source_zsh` or `source_fish`\n\n### Configuration\n\nMake a copy of the environment config example file:\n\n    cp .env.example .env\n\nEdit `.env` to suit your needs, then:\n\n    export $(grep -v \'^#\' .env | xargs -d \'\\n\')\n\nMake a copy of the Ansible inventory example file:\n\n    cp hosts.yaml.example hosts.yaml\n\nEdit `hosts.yaml` to suit your needs.\n\nMake a copy of the MADAM config example file:\n\n    cp madam.yaml.example madam.yaml\n\nEdit `madam.yaml` to suit your needs.\n\nMake a copy of the MADAM config example file for the test environment:\n\n    cp madam_tests.yaml.example madam_tests.yaml\n\nEdit `madam_tests.yaml` to suit your needs.\n\nMake a copy of the MADAM config example file for the local deploy:\n\n    cp madam_deploy.yaml.example madam_deploy.yaml\n\nEdit `madam_deploy.yaml` to suit your needs.\n\n### Set and tag project version in Git\n\n    ./bin/release.sh 1.0.0\n\n### Build MADAM python package and Docker image\n\n    make build\n\nThe wheel package will be build in the `dist` directory.\n\n## Deploy MADAM as local docker container\n\nTo deploy MADAM container on localhost:\n\n    make deploy\n\n## Check static type and code quality\n\n    make check\n\n## Run tests\n\nRun all [pytest](https://docs.pytest.org) tests with:\n\n    make tests\n\nRun only some tests by using `bin/tests.sh`:\n\n    bin/tests.sh tests/domains/test_workflows.py::test_create\n\n## Database setup\n\nSet `DATABASE_URL` and `DATABASE_URL_TESTS` environment variable in `.env` file:\n\n    DATABASE_URL=postgresql://postgres:xxxxx@hostname:5432/madam?sslmode=allow\n    DATABASE_URL_TESTS=postgresql://postgres:xxxxx@hostname:5432/madam_tests?sslmode=allow\n\n### Migrations scripts\n\nAdd/Edit scripts in `resources/migrations` directory:\n\n    # version.name.[rollback].sql\n    00001.init_tables.sql\n    00001.init_tables.rollback.sql\n\n### Migrate commands\n\n    make databases\n    make databases_rollback\n    make databases_list\n',
    'author': 'Vincent Texier',
    'author_email': 'vit@free.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
