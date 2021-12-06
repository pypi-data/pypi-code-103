# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ops2deb']

package_data = \
{'': ['*'], 'ops2deb': ['templates/*']}

install_requires = \
['aiofiles',
 'httpx>=0.20.0,<0.22.0',
 'jinja2',
 'pydantic',
 'python-debian>=0.1.42,<0.2.0',
 'ruamel.yaml>=0.17.16,<0.18.0',
 'semver==3.0.0-dev.2',
 'typer']

entry_points = \
{'console_scripts': ['ops2deb = ops2deb.cli:main']}

setup_kwargs = {
    'name': 'ops2deb',
    'version': '0.11.1',
    'description': 'Build debian packages',
    'long_description': "[![upciti](https://circleci.com/gh/upciti/ops2deb.svg?style=svg)](https://circleci.com/gh/upciti/ops2deb)\n[![codecov](https://codecov.io/gh/upciti/ops2deb/branch/main/graph/badge.svg)](https://codecov.io/gh/upciti/ops2deb)\n[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)\n[![Generic badge](https://img.shields.io/badge/type_checked-mypy-informational.svg)](https://mypy.readthedocs.io/en/stable/introduction.html)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/ops2deb.svg)](https://pypi.python.org/pypi/ops2deb/)\n[![Downloads](https://static.pepy.tech/personalized-badge/ops2deb?period=total&units=international_system&left_color=blue&right_color=green&left_text=Downloads)](https://pepy.tech/project/ops2deb)\n\n# ops2deb\n\nAre you tired of checking if your favorite devops tools are up-to-date? Are you using a debian based GNU/Linux distribution?\n`ops2deb` is designed to generate Debian packages for common devops tools such as kubectl, kustomize, helm, ...,\nbut it could be used to package any statically linked application. In short, it consumes a configuration file and outputs `.deb` packages.\n\n## Configuration file\n\nWritten in YAML and composed of a list of package blueprints. A blueprint is defined by the following:\n\n| Field         | Meaning                                                                                                                                     | Default |\n| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- |\n| `name`        | Component name, e.g. `kustomize`.                                                                                                           |         |\n| `version`     | Application release to package.                                                                                                             |         |\n| `homepage`    | Upstream project homepage.                                                                                                                  | `None`  |\n| `arch`        | Package architecture.                                                                                                                       | `amd64` |\n| `revision`    | Package revistion.                                                                                                                          | `1`     |\n| `summary`     | Package short description.                                                                                                                  |         |\n| `description` | Package full description.                                                                                                                   |         |\n| `fetch`       | A binary to download, and a `sha256` checksum. `tar.gz`, `tar.xz`, `tar` and `zip` (requires `unzip`) archives are extracted automatically. | `Null`  |\n| `script`      | List of build instructions templated with jinja2 and intepreted with the default `shell`.                                                   | `[]`    |\n| `depends`     | List of package dependencies. Corresponds to `Depends` entry in `debian/control`.                                                           | `[]`    |\n| `recommends`  | List of package recommended dependencies. Corresponds to `Recommends` entry in `debian/control`.                                            | `[]`    |\n| `conflicts`   | List of conflicting packages. Corresponds to `Conflicts` entry in `debian/control`.                                                         | `[]`    |\n\nExample:\n\n```yaml\n- name: kubectl\n  version: 1.20.1\n  summary: Command line client for controlling a Kubernetes cluster\n  description: |\n    kubectl is a command line client for running commands against Kubernetes clusters.\n  fetch:\n    url: https://storage.googleapis.com/kubernetes-release/release/v{{version}}/bin/linux/amd64/kubectl\n    sha256: 3f4b52a8072013e4cd34c9ea07e3c0c4e0350b227e00507fb1ae44a9adbf6785\n  script:\n    - mv kubectl {{src}}/usr/bin/\n```\n\n## Dependencies\n\n- Python >= 3.9\n- To build debian packages with `ops2deb build` you need the following packages on your host:\n\n```shell\nsudo apt install build-essential fakeroot debhelper\n```\n\n## Usage example\n\nInstall `ops2deb` in a virtualenv or with [pipx](https://github.com/pipxproject/pipx)\n\n```shell\npipx install ops2deb\n```\n\nThen, in a test directory run:\n\n```shell\ncurl https://raw.githubusercontent.com/upciti/ops2deb/main/ops2deb.yml\nops2deb generate\nops2deb build\n```\n\nTo check for new releases run:\n\n```shell\nops2deb update\n```\n\n`ops2deb` uses temp directories to cache downloaded binaries and to run build instructions:\n\n```shell\ntree /tmp/ops2deb_*\n```\n\nThe cache can be flushed with:\n\n```shell\nops2deb purge\n```\n\n## Development\n\nYou will need [poetry](https://python-poetry.org/)\n\n```shell\npoetry install\npoetry run task check\n```\n\n## Important notes\n\n`ops2deb` **DOES NOT** sandbox build instructions so if you do something like:\n\n```shell\nscript:\n- rm -rf ~/*\n```\n\nYou will loose your files... To make sure that you won't mess with your system, run it within a container.\n",
    'author': 'Upciti',
    'author_email': 'support@upciti.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/upciti/ops2deb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
