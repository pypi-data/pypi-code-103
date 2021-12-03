# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nautilus_librarian',
 'nautilus_librarian.mods',
 'nautilus_librarian.mods.dvc',
 'nautilus_librarian.mods.dvc.domain',
 'nautilus_librarian.mods.dvc.typer',
 'nautilus_librarian.mods.git',
 'nautilus_librarian.mods.git.domain',
 'nautilus_librarian.mods.git.typer',
 'nautilus_librarian.mods.gpg',
 'nautilus_librarian.mods.gpg.domain',
 'nautilus_librarian.mods.gpg.typer',
 'nautilus_librarian.mods.libvips',
 'nautilus_librarian.mods.libvips.domain',
 'nautilus_librarian.mods.libvips.typer',
 'nautilus_librarian.mods.namecodes',
 'nautilus_librarian.mods.namecodes.domain',
 'nautilus_librarian.mods.namecodes.typer',
 'nautilus_librarian.typer']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.24',
 'PyGithub>=1.55',
 'dvc[azure]>=2.8.3,<3.0.0',
 'mypy>=0.910,<0.911',
 'pyvips>=2.1.16',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['nautilus-librarian = nautilus_librarian.main:app']}

setup_kwargs = {
    'name': 'nautilus-librarian',
    'version': '0.1.0',
    'description': 'A Python Console application to handle media libraries like Git and DVC',
    'long_description': '# Nautilus Librarian\n\n[![Lint Code Base](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/linter.yml/badge.svg)](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/linter.yml)[![Publish Docker image](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/publish-docker-image.yml/badge.svg)](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/publish-docker-image.yml)[![Test](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/test.yml/badge.svg)](https://github.com/Nautilus-Cyberneering/librarian/actions/workflows/test.yml)\n\nA Python Console application to handle media libraries like Git and [Dvc](https://github.com/iterative/dvc).\n\n## Development\n\n### Run\n\nWith docker:\n\nBuild:\n\n```shell\n./bin/docker/build.sh\n```\n\nRun pre-built docker image:\n\n```shell\n./bin/docker/run.sh [OPTIONS] COMMAND [ARGS]...\n./bin/docker/run.sh --help\n```\n\nRun mounting current repo:\n\n```shell\n./bin/docker/run-dev.sh [OPTIONS] COMMAND [ARGS]...\n./bin/docker/run-dev.sh --help\n```\n\nWith Poetry:\n\n```shell\npoetry install\npoetry run nautilus-librarian [OPTIONS] COMMAND [ARGS]...\npoetry run nautilus-librarian --help\n```\n\n> NOTE: With Poetry, you have to install the [Librarian system dependencies](https://github.com/Nautilus-Cyberneering/librarian-system-dockerfile).\n\n### Testing\n\nWith docker:\n\n```shell\n./bin/docker/test.sh\n```\n\nWith Poetry:\n\n```shell\npoetry shell\npytest\n```\n\nor:\n\n```shell\npoetry run pytest --cov\n```\n\n### Linting\n\nFor Dockerfile:\n\nWe are using GitHub Action [super-linter](https://github.com/marketplace/actions/super-linter). If you want to check the `Dockerfile` linting before pushing, you can do it with:\n\n```shell\ndocker run --rm -i hadolint/hadolint < Dockerfile\n```\n\nRun super-linter locally with [act](https://github.com/nektos/act):\n\n```shell\nact -W .github/workflows/linter.yml -j build\n```\n',
    'author': 'Jose Celano',
    'author_email': 'jose@nautilus-cyberneering.de',
    'maintainer': 'Jose Celano',
    'maintainer_email': 'jose@nautilus-cyberneering.de',
    'url': 'https://github.com/Nautilus-Cyberneering/librarian',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
