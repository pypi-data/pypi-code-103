# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplematrixbotlib']

package_data = \
{'': ['*']}

install_requires = \
['markdown>=3.3',
 'matrix-nio>=0.18',
 'pillow>=8.2',
 'python-cryptography-fernet-wrapper>=1.0.4',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'simplematrixbotlib',
    'version': '2.4.1',
    'description': 'An easy to use bot library for the Matrix ecosystem written in Python.',
    'long_description': '# Simple-Matrix-Bot-Lib\n(Version 2.4.1)\n\nSimple-Matrix-Bot-Lib is a Python bot library for the Matrix ecosystem built on [matrix-nio](https://github.com/poljar/matrix-nio).\n\n[View on Github](https://github.com/KrazyKirby99999/simple-matrix-bot-lib) or [View on PyPi](https://pypi.org/project/simplematrixbotlib/) or\n[View docs on readthedocs.io](https://simple-matrix-bot-lib.readthedocs.io/en/latest/)\n\nLearn how you can contribute [here](CONTRIBUTING.md).\n\n## Installation\n\n### simplematrixbotlib can be either installed from PyPi or downloaded from github.<br>\n\nInstallation from PyPi:\n\n```\npython -m pip install simplematrixbotlib\n```\n\nDownload from github:\n\n```\ngit clone --branch master https://github.com/KrazyKirby99999/simple-matrix-bot-lib.git\n```\n\n## Example Usage\n\n```python\n# echo.py\n# Example:\n# randomuser - "!echo example string"\n# echo_bot - "example string"\n\nimport simplematrixbotlib as botlib\n\ncreds = botlib.Creds("https://home.server", "echo_bot", "pass")\nbot = botlib.Bot(creds)\nPREFIX = \'!\'\n\n@bot.listener.on_message_event\nasync def echo(room, message):\n    match = botlib.MessageMatch(room, message, bot, PREFIX)\n\n    if match.is_not_from_this_bot() and match.prefix() and match.command("echo"):\n\n        await bot.api.send_text_message(\n            room.room_id, " ".join(arg for arg in match.args())\n            )\n\nbot.run()\n```\n\nMore information and examples can be found [here](https://simple-matrix-bot-lib.readthedocs.io/en/latest/).',
    'author': 'krazykirby99999',
    'author_email': 'krazykirby99999@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/KrazyKirby99999/simple-matrix-bot-lib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
