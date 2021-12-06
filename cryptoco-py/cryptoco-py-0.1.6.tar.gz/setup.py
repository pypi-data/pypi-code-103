# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cryptoco_py']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['cryptoco-py = cryptoco_py.__main__:app']}

setup_kwargs = {
    'name': 'cryptoco-py',
    'version': '0.1.6',
    'description': 'A package to query cryptocurrency information',
    'long_description': '\n\n# CryptoCo-py\n\n[CryptoCo-py](https://github.com/Edmain1/CryptoCo-py) is a Python CLI application that uses [CoinGecko](https://www.coingecko.com/en/api) API to allow the user to query cryptocurrency information\nby typing simple commands.\n\n#### Table of contents\n- [Installation](#installation)\n- [Requirements](#requirements)\n- [Usage](#usage)\n- [License](#license)\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install cryptoco-py.\n\n```bash\npip install cryptoco-py\n```\n## Requirements\n| Name      | Version |\n| :-----------: | :-----------: |\n| [Python](https://www.python.org/)      | 3.6 +       |\n| [Typer](https://typer.tiangolo.com/)   | 0.4.0 +        |\n| [Requests](https://docs.python-requests.org/en/latest/) | 2.26.0 +        |\n\n\n## Usage\n\n```bash\n# pings the server\ncryptoco-py [OPTIONS] COMMAND [ARGS]...\n```\n\n>NOTE: you might not be able to run the command instantly after installing it\n>to solve this problem simply add the directory of the installed package to ```$PATH```\n\n```bash\n# returns a help message\ncryptoco-py --help\n```\nyou can also write the output to an output file for example:\n```bash\ncryptoco-py sprice bitcoin > output.txt\n\ncat output.txt\n# output:\n{\n  "bitcoin": {\n    "usd": 48338\n  }\n}\n\n```\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'Jawad Abduljawad(TerminalJ)',
    'author_email': 'jawadhamdiabduljawad@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Edmain1/CryptoCo-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
