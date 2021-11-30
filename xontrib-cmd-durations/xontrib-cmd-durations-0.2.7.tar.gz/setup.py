# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xontrib']

package_data = \
{'': ['*']}

install_requires = \
['xonsh>=0.10']

extras_require = \
{':python_version >= "3.6" and python_version < "4.0"': ['notify-py>=0.3.3']}

setup_kwargs = {
    'name': 'xontrib-cmd-durations',
    'version': '0.2.7',
    'description': 'Send notification once long running command is finished. Add duration PROMP_FIELD.',
    'long_description': '## Overview\n\n<p align="center">\nSend notification once long-running command is finished and also show the execution time..\n</p>\n\n## Installation\n\nTo install use pip:\n\n``` bash\nxpip install xontrib-cmd-durations\n# or: xpip install -U git+https://github.com/jnoortheen/xontrib-cmd-durations\n```\n\n## Usage\n\nAdd the `long_cmd_duration` section to the [prompt fields](https://xon.sh/tutorial.html#customizing-the-prompt) and load the xontrib i.e.:\n\n``` bash\n$RIGHT_PROMPT = \'{long_cmd_duration:⌛{}}{user:{{BOLD_RED}}🤖{}}{hostname:{{BOLD_#FA8072}}🖥{}}\'\n$XONRTIB_CD_LONG_DURATION = 5  # default\nxontrib load cmd_done\n```\n\nIf the command is taking more than `$XONRTIB_CD_LONG_DURATION` seconds then `long_cmd_duration` returns the duration in human readable way:\n\n![](./images/2020-10-26-10-59-38.png)\n\nThe desktop notification is sent if the terminal is not focused:\n\n![](./images/2020-11-02-13-38-47.png)\n\nCurrently the focusing part requires `xdotool` to be installed.\n\n## Known issues\n\n### notifications in Windows\nOn windows the notification will get triggered all the time. \n`Finding whether the terminal is focused` is not implemented for Windows yet and PRs are very welcome on that.\nSet `$XONRTIB_CD_TRIGGER_NOTIFICATION = False` to completely off the notification part.\n\n\n## Credits\n\nThis package was created with [xontrib cookiecutter template](https://github.com/jnoortheen/xontrib-cookiecutter).\n',
    'author': 'Noortheen Raja J',
    'author_email': 'jnoortheen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jnoortheen/xontrib-cmd-durations',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
