# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['workspace',
 'workspace.cli',
 'workspace.cli.commands',
 'workspace.cli.commands.template',
 'workspace.core',
 'workspace.core.adapter',
 'workspace.templates.pipenv.{{ cookiecutter.project_slug }}.{{ '
 'cookiecutter.package_name }}',
 'workspace.templates.poetry.{{ cookiecutter.project_slug }}.{{ '
 'cookiecutter.package_name }}']

package_data = \
{'': ['*'],
 'workspace': ['templates/pipenv/*',
               'templates/pipenv/{{ cookiecutter.project_slug }}/*',
               'templates/poetry/*',
               'templates/poetry/{{ cookiecutter.project_slug }}/*']}

install_requires = \
['click>=8.0,<9.0', 'jsonschema>=4.0.1,<5.0.0']

extras_require = \
{'cookiecutter': ['cookiecutter>=1.7.3,<2.0.0'],
 'pipenv': ['pipenv>=2021.5.29,<2022.0.0'],
 'poetry': ['poetry>=1.1.11,<2.0.0']}

entry_points = \
{'console_scripts': ['workspace = workspace.__main__:run_cli']}

setup_kwargs = {
    'name': 'workspace-cli',
    'version': '0.3.0',
    'description': 'Manage interdependent projects in a workspace.',
    'long_description': '# Workspace\n\n**Workspace** streamlines management and adoption of mono-repositories, by providing a wrapper around multi-repo tooling.\n\nIt was initially implemented to manage Python projects, but can be extended to interpret other types of projects.\n\n## Documentation\n\n- [Home](https://jacksmith15.github.io/workspace-cli/)\n    + [Installation](https://jacksmith15.github.io/workspace-cli/installation/)\n    + [Configuration](https://jacksmith15.github.io/workspace-cli/configuration/)\n    + [Basic usage](https://jacksmith15.github.io/workspace-cli/basic-usage/)\n    + [Templates](https://jacksmith15.github.io/workspace-cli/templates/)\n    + [Plugins](https://jacksmith15.github.io/workspace-cli/plugins/)\n    + [FAQ](https://jacksmith15.github.io/workspace-cli/faq/)\n\n\n## Development\n\nInstall dependencies:\n\n```shell\npyenv shell 3.8.6  # Or other version >= 3.8\npre-commit install  # Configure commit hooks\npoetry install  # Install Python dependencies\n```\n\nRun tests:\n\n```shell\npoetry run inv verify\n```\n\n### Todos\n\n- [ ] Experiment with non-Python workspaces\n- [ ] More detailed plugin documentation\n- [ ] Example workspaces\n- [ ] Test output on shells with limited color support\n- [ ] Labelling projects\n- [ ] Project aliases\n\n## License\n\nThis project is distributed under the MIT license.\n',
    'author': 'Jack Smith',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jacksmith15/workspace-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
