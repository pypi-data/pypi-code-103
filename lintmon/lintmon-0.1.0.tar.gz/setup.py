# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lintmon']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0', 'psutil>=5.8.0']

entry_points = \
{'console_scripts': ['lintmon-run-all = lintmon:run_all',
                     'lintmon-start = lintmon:start',
                     'lintmon-status = lintmon:status',
                     'lintmon-status-prompt = lintmon:status_prompt',
                     'lintmon-stop = lintmon:stop',
                     'lintmond = lintmon:lintmond']}

setup_kwargs = {
    'name': 'lintmon',
    'version': '0.1.0',
    'description': 'Monitor project files in the background for lint issues and flag issues in your prompt',
    'long_description': '# lintmon\n\nA tool for monitoring for lint errors. Provides a configurable way to specify checks to run on code in a given directory when it changes on disk, run those checks in the background and provide a fast way to display the outcome of the latest checks with a concise format suitable for embedding in your prompt.\n\nIt is designed for lint errors because these are quick to run and affect single files at a time, so in general they can be checked in the background with relatively low system impact, but in principle you could use it to trigger any sort of validation check, such as running unit tests.\n\n## Motivation\n\nThe two main ways of avoiding pushing lint errors to a repo it seemed to me were:\n\n1. lint on save in your IDE\n2. add git hooks on push to check for / fix lint errors\n\nI didn\'t like either of those, because in both cases they happen synchronously while you are doing something and can cause disruptions. Also I push from the command line, so what I wanted was a warning at the point that I was going to push that was pre-calculated about errors.\n\nThis is that.\n\n## Configure\n\nInstall lintmon using `pip` in your virtualenv (or wherever you install packages for use with your codebase):\n\n    pip install lintmon\n\nAdd a file like the lintmon.yaml file in this codebase to the root directory of your codebase. It tells dirmmon what checks to do on files. It aims to be very configurable.\n\nAdd the following to your prompt in your `.bashrc` or `.zshrc`:\n\n    PS1=\'$([[ -e lintmon.yaml ]] && which lintmon-status-prompt >/dev/null && lintmon-status-prompt)\'$PS1\n\nThat\'s it! `lintmon-status-prompt` will start `lintmond` automatically in the background when it is run, and from now on you should get a "badge" in your prompt when there are lint errors in your directory, which will be updated when you modify files.\n\n## Commands\n\n### `lintmon-status`\n\nOutput status of lintmon along with all current errors from the linters.\n\n### `lintmon-stop`, `lintmon-start`\n\nTell lintmon to stop (and not restart automatically) or start again. Mostly useful for debugging lintmon. This will display an ` S ` badge in your prompt to tell you it is stopped.\n\n### `lintmon-run-all`\n\nRun all linters on all appropriate files in your project, thus "hydrating" lintmon\'s state if it hasn\'t been running for a while and changes have been made.\n\n### `lintmond`\n\nRun the daemon in the shell (again mainly useful for debugging).\n\n\n## Directory structure\n\nlintmon adds a `.lintmon` directory to your project directory where it stores all its state about what current errors there are, lintmon\'s pid etc. You will probably want to add this to your .gitignore.\n',
    'author': 'David Park',
    'author_email': 'david@greenparksoftware.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daphtdazz/lintmon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
