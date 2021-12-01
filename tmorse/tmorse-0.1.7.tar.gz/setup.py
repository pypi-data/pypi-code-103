# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tmorse']

package_data = \
{'': ['*'], 'tmorse': ['data/*']}

entry_points = \
{'console_scripts': ['tmorse = tmorse.__main__:run']}

setup_kwargs = {
    'name': 'tmorse',
    'version': '0.1.7',
    'description': 'Blinking Morse code on Thinkpad LEDs',
    'long_description': '# TMorse\n\nRun this code to blink your ThinkPad LED with a hidden mysterious Morse code! ;)\\\nCompatible with python3.9+. No third-party library is required, implemented in pure python.\\\nMake sure that you have required permissions to write to led acpi file descriptor.\n\n# Take a look\n\n![LED](./pics/LED.gif)\n![Backlit](./pics/Backlit.gif)\n![Decode](./pics/Decode.gif)\n\n## Installation\n\nInstallation of tmorse is a little complicated due to need of superuser access.\\\nRecommended way is using [pipx](https://github.com/pypa/pipx).\nFirst, install pipx:\n\n```bash\nsudo apt install pipx\n```\n\nThen install tmorse by using command below:\n\n```bash\nsudo -E env "PATH=$PATH" pipx install --python python3.9 tmorse\n```\n\nP.S: TMorse is supported by python3.9+.\n\n## Usage\n\n```bash\nsudo tmorse\n```\n→ Insert input manually, and it will blink your LED, which its location is defined by default to be `/proc/acpi/ibm/led`.\n\n```bash\necho "This is a test" | sudo tmorse --stdin\n```\n→ Read the data from standard input.\n```bash\nsudo tmorse -c custom_codes.json\n```\n→  Encode characters to Morse based on your custom codes, although you should follow the protocol. (e.g. {"م": "--"})\n```bash\nsudo tmorse --on-command 2 --off-command 0 -l "/proc/acpi/ibm/kbdlight" -m 0.7 --default-led-status OFF\n```\n→ Show the Morse code by keyboard\'s backlit blinking.\n\n- check `sudo tmorse --help` for more info.\n\n\n\n## Contributing\n    Written by: Mahyar Mahdavi <Mahyar@Mahyar24.com>.\n    License: GNU GPLv3.\n    Source Code: <https://github.com/mahyar24/TMorse>.\n    PyPI: <https://pypi.org/project/TMorse/>.\n    Reporting Bugs and PRs are welcomed. :)\n\n## Inspired by \nThis Project is based and inspired by "[Ritvars Timermanis](https://ritvars.lv/)" thinkmorse.\nTake a look at: [thinkmorse](https://github.com/RichusX/thinkmorse).\n\n## License\n[GPLv3](https://choosealicense.com/licenses/gpl-3.0)\n',
    'author': 'Mahyar Mahdavi',
    'author_email': 'Mahyar@Mahyar24.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mahyar24/TMorse/',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
