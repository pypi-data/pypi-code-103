# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['delfino', 'delfino.commands', 'delfino.models']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pydantic>=1.8.2,<2.0.0', 'toml>=0.10.2,<0.11.0']

extras_require = \
{'all': ['black',
         'isort',
         'pre-commit',
         'pytest',
         'coverage',
         'pytest-cov',
         'pytest-dotenv',
         'pytest-mock',
         'mypy',
         'pylint',
         'pycodestyle',
         'pydocstyle',
         'twine'],
 'format': ['black', 'isort', 'pre-commit'],
 'lint': ['pylint', 'pycodestyle', 'pydocstyle'],
 'test': ['pytest', 'coverage', 'pytest-cov', 'pytest-dotenv', 'pytest-mock'],
 'typecheck': ['mypy'],
 'upload_to_pypi': ['twine'],
 'verify_all': ['black',
                'isort',
                'pre-commit',
                'pytest',
                'coverage',
                'pytest-cov',
                'pytest-dotenv',
                'pytest-mock',
                'mypy',
                'pylint',
                'pycodestyle',
                'pydocstyle']}

entry_points = \
{'console_scripts': ['delfino = delfino.main:main', 'mike = delfino.main:main']}

setup_kwargs = {
    'name': 'delfino',
    'version': '0.8.1',
    'description': 'A collection of command line helper scripts wrapping tools used during Python development.',
    'long_description': '<h1 align="center" style="border-bottom: none;">🧰&nbsp;&nbsp;Delfino&nbsp;&nbsp;🧰</h1>\n<h3 align="center">A collection of command line helper scripts wrapping tools used during Python development.</h3>\n\n<p align="center">\n    <a href="https://app.circleci.com/pipelines/github/radeklat/delfino?branch=main">\n        <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/radeklat/delfino">\n    </a>\n    <a href="https://app.codecov.io/gh/radeklat/delfino/">\n        <img alt="Codecov" src="https://img.shields.io/codecov/c/github/radeklat/delfino">\n    </a>\n    <a href="https://github.com/radeklat/delfino/tags">\n        <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/tag/radeklat/delfino">\n    </a>\n    <img alt="Maintenance" src="https://img.shields.io/maintenance/yes/2021">\n    <a href="https://github.com/radeklat/delfino/commits/main">\n        <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/radeklat/delfino">\n    </a>\n</p>\n\n<!--\n    How to generate TOC from PyCharm:\n    https://github.com/vsch/idea-multimarkdown/wiki/Table-of-Contents-Extension\n-->\n[TOC levels=1,2 markdown formatted bullet hierarchy]: # "Table of content"\n\n# Table of content\n- [Installation](#installation)\n- [Usage](#usage)\n\n# Installation\n\nTODO\n\n# Usage\n\nTODO\n\n<!--\n\n## Minimal plugin\n\n```python\nimport click\n\nfrom delfino.contexts import pass_app_context, AppContext\n\n\n@click.command()\n@pass_app_context\ndef plugin_test(app_context: AppContext):\n    """Tests commands placed in the `commands` folder are loaded."""\n    print(app_context.py_project_toml.tool.delfino.plugins)\n```\n\n -->\n\n<!--\n\n# Install completions\n\nBased on [Click documentation](https://click.palletsprojects.com/en/8.0.x/shell-completion/?highlight=completions#enabling-completion) and Invoke implementation of dynamic completion:\n\n```bash\n# Invoke tab-completion script to be sourced with Bash shell.\n# Known to work on Bash 3.x, untested on 4.x.\n\n_complete_invoke() {\n    local candidates\n\n    # COMP_WORDS contains the entire command string up til now (including\n    # program name).\n    # We hand it to Invoke so it can figure out the current context: spit back\n    # core options, task names, the current task\'s options, or some combo.\n    candidates=`invoke --complete -- ${COMP_WORDS[*]}`\n\n    # `compgen -W` takes list of valid options & a partial word & spits back\n    # possible matches. Necessary for any partial word completions (vs\n    # completions performed when no partial words are present).\n    #\n    # $2 is the current word or token being tabbed on, either empty string or a\n    # partial word, and thus wants to be compgen\'d to arrive at some subset of\n    # our candidate list which actually matches.\n    #\n    # COMPREPLY is the list of valid completions handed back to `complete`.\n    COMPREPLY=( $(compgen -W "${candidates}" -- $2) )\n}\n\n\n# Tell shell builtin to use the above for completing our invocations.\n# * -F: use given function name to generate completions.\n# * -o default: when function generates no results, use filenames.\n# * positional args: program names to complete for.\ncomplete -F _complete_invoke -o default invoke inv\n```\n\nPut into `~/.bashrc`:\n\n```bash\n_complete_delfino() {\n    eval "$(_DELFINO_COMPLETE=bash_source delfino)";\n}\ncomplete -F _complete_delfino -o default invoke delfino\n```\n\n-->',
    'author': 'Radek Lát',
    'author_email': 'radek.lat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/radeklat/delfino',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
