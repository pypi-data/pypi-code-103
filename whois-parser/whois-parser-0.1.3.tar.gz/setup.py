# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whois_parser', 'whois_parser.parsers']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json==0.5.5', 'dateparser>=1.1.0,<2.0.0', 'pyparsing==3.0.6']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8.2,<5.0.0']}

setup_kwargs = {
    'name': 'whois-parser',
    'version': '0.1.3',
    'description': 'Yet another whois parser for Python',
    'long_description': '# whois-parser\n\n[![PyPI version](https://badge.fury.io/py/whois-parser.svg)](https://badge.fury.io/py/whois-parser)\n[![Python CI](https://github.com/ninoseki/whois-parser/actions/workflows/test.yml/badge.svg)](https://github.com/ninoseki/whois-parser/actions/workflows/test.yml)\n[![Coverage Status](https://coveralls.io/repos/github/ninoseki/whois-parser/badge.svg?branch=main)](https://coveralls.io/github/ninoseki/whois-parser?branch=main)\n\nYet another whois parser for Python. 🐍\n\n- Parse a whois record by using [PyParsing](https://github.com/pyparsing/pyparsing/) not Regex.\n- Return a parsed record as [dataclass](https://docs.python.org/3/library/dataclasses.html) not dict.\n\n## Installation\n\n```bash\npip install whois-parser\n```\n\n## Usage\n\n```python\nimport sh\nfrom whois_parser import WhoisParser\n\n# get whois record\nhostname = "google.co.jp"\nwhois = sh.Command("whois")\nraw_text = whois(hostname)\n\n# parse whois record\nparser = WhoisParser()\nrecord = parser.parse(raw_text, hostname=hostname)\nprint(record)\n# => WhoisRecord(raw_text="...", registrant=Registrant(organization=\'グーグル合同会社\', email=None, name=None, telephone=None), admin=Admin(organization=None, email=None, name=None, telephone=None), tech=Tech(organization=None, email=None, name=None, telephone=None), abuse=Abuse(email=None, telephone=None), statuses=[\'Connected (2022/03/31)\'], name_servers=[\'ns1.google.com\', \'ns2.google.com\', \'ns3.google.com\', \'ns4.google.com\'], domain=\'google.co.jp\', registrar=None, expires_at=None, registered_at=datetime.datetime(2001, 3, 22, 0, 0), updated_at=datetime.datetime(2021, 4, 1, 1, 5, 22, tzinfo=<StaticTzInfo \'JST\'>))\n```\n\n## Customize / Contribution\n\nWhois\'s responses will follow a semi-free text format. Thus, unfortunately, this library does not support all the formats in the wild.\n\nYou can create customized parsers to suit your needs. References are placed in `whois-parser/parsers/`.\n\nAny contribution is welcome.\n',
    'author': 'Manabu Niseki',
    'author_email': 'manabu.niseki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ninoseki/whois-parser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
