# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aib2ofx']

package_data = \
{'': ['*']}

install_requires = \
['mechanicalsoup>=1.1,<2.0', 'python-dateutil>=2.8.1,<3.0.0']

entry_points = \
{'console_scripts': ['aib2ofx = aib2ofx.cli:main']}

setup_kwargs = {
    'name': 'aib2ofx',
    'version': '0.73.1',
    'description': 'Download data from aib.ie in OFX format',
    'long_description': '# aib2ofx\n\n...or how to grab transaction data out of AIB\'s online interface, and format it\ninto `OFX` file.\n\n**NOTE:** Last AIB login update (Feb\' 2021) made me realise how brittle the\noverall machinery here is. The code that works around Web Storage API use is\nugly and likely to break. The most likely road forward for this project is to\ndecouple it into [ofxstatement](https://github.com/kedder/ofxstatement) plugin\nand (maybe) Selenium-powered CSV acquisition script. The former will be easy,\nthe latter will most likely be a nightmare to maintain and install, unless you\nenjoy having your banking details pipe through an arbitrary docker image.\n\nTime will tell.\n\n## Installation\n\n    python3 -mvenv aib2ofx\n    source aib2ofx/bin/activate\n    pip3 install aib2ofx\n\nThis will create a virtualenv for `aib2ofx`, fetch its code then install it with\nall dependencies. Once that completes, you\'ll find `aib2ofx` executable in the\n`bin` directory of this new virtualenv.\n\n## Usage\n\nCreate a `~/.aib2ofx.json` file, with AIB login details.\nSet the permission bits to 0600 to prevent other system users from reading it.\n\n    touch ~/.aib2ofx.json\n    chmod 0600 ~/.aib2ofx.json\n\nIt has a JSON format, single object with one key per AIB login you want to use.\n\n    {\n        "bradmajors": {\n            "regNumber": "12345678",\n            "pin": "12345"\n        }\n    }\n\nThe fields are as follows:\n\n* regNumber\n    > Your AIB registered number.\n\n* pin\n    > Your five digit PIN.\n\nYou can put more than one set of credentials in the file; the script\nwill download data for all accounts for all logins.\n\n    {\n        "bradmajors": {\n            "regNumber": "12345678",\n            "pin": "12345"\n        },\n        "janetweiss": {\n            "regNumber": "87654321",\n            "pin": "54321"\n        }\n    }\n\nNote that there\'s no comma after the last account details.\n\nOnce you\'ve prepared that config file, run:\n\n    aib2ofx -d /output/directory\n\nThe script should connect to AIB, log in using provided credentials,\niterate through all accounts, and save each of those to a separate\nfile located in `/output/directory`.\n\n## Guarantee\n\nThere is none.\n\nI\'ve written that script with my best intentions, it\'s not malicious,\nit\'s not sending the data anywhere, it\'s not doing anything nasty. I\'m\nusing it day to day to get data about my AIB accounts into a financial\nprogram that I use. It should work for you as good as it works for\nme. See the `LICENSE` file for more details.\n\n## Development\n\naib2ofx works only with python 3.\n\nIn order to set up a dev environment clone the repository, get\n[poetry](https://python-poetry.org/docs/#installation)\nand run `poetry install`. This will create a virtualenv with all\ndependencies installed. You can activate it with `poetry shell`.\n',
    'author': 'Jakub Turski',
    'author_email': 'yacoob@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yacoob/aib2ofx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
