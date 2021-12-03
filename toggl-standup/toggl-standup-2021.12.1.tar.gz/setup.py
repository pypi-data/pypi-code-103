# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['togglstandup']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.1,<8.0.0',
 'humanfriendly>=10.0,<11.0',
 'maya>=0.6.1,<0.7.0',
 'rich>=10.15.2,<11.0.0',
 'togglwrapper>=2.0.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['standup = togglstandup.cli:cli']}

setup_kwargs = {
    'name': 'toggl-standup',
    'version': '2021.12.1',
    'description': 'Removes the pain of using Toggl with Geekbot',
    'long_description': '# Stand Up for Toggl\n\nThis tool helps generate my daily Geekbot stand up report in an format which I may copy and paste into Slack.\n\n## Usage\n<!-- [[[cog\nimport cog\nfrom typer.testing import CliRunner\nfrom togglstandup.cli import cli\nrunner = CliRunner()\nresult = runner.invoke(cli, ["--help"])\nhelp = result.output.replace("Usage: main", "Usage: standup")\ncog.outl("```shell")\ncog.outl("$ export TOGGL_API_KEY=\'PASTE_YOUR_KEY_HERE\'\\n")\ncog.outl("$ standup --help\\n")\ncog.outl("{}```".format(help))\n]]] -->\n```shell\n$ export TOGGL_API_KEY=\'PASTE_YOUR_KEY_HERE\'\n\n$ standup --help\n\nUsage: standup [OPTIONS] SLANG_DATE\n\n  Standup tool to help with Toggl\n\nArguments:\n  SLANG_DATE  [required]\n\nOptions:\n  --api-key TEXT                  [default: ]\n  --show-duration / --no-show-duration\n                                  [default: False]\n  --show-time / --no-show-time    [default: False]\n  --timezone TEXT                 [default: US/Central]\n  --version\n  --install-completion            Install completion for the current shell.\n  --show-completion               Show completion for the current shell, to copy\n                                  it or customize the installation.\n\n  --help                          Show this message and exit.\n```\n<!-- [[[end]]] -->\n\n## To generate a report for yesterday\n\n```shell\n$ standup yesterday\n```\n',
    'author': 'Jeff Triplett',
    'author_email': 'jeff.triplett@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jefftriplett/toggl-standup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
