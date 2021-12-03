# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyvultr', 'pyvultr.utils', 'pyvultr.v2']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'dacite>=1.6.0,<2.0.0',
 'fire>=0.4.0,<0.5.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['pyvultr = pyvultr.cli:main']}

setup_kwargs = {
    'name': 'pyvultr',
    'version': '0.1.3',
    'description': 'Python library for Vultr API',
    'long_description': '## Python Library for [Vultr](https://www.vultr.com/) API\n\nThe unofficial python library for the Vultr API.\n\n[![CI](https://github.com/luxiaba/pyvultr/actions/workflows/ci.yaml/badge.svg)](https://github.com/luxiaba/pyvultr/actions/workflows/ci.yaml)\n[![PyPI](https://img.shields.io/pypi/v/pyvultr?color=blue&label=PyPI)](https://pypi.org/project/pyvultr/)\n\n[![Python 3.6.8](https://img.shields.io/badge/python-3.6.8-blue.svg)](https://www.python.org/downloads/release/python-368/)\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n\n### Installation\n```\npip install -U pyvultr\n```\n\n### Usage\n\n#### Configuration\n```python\nfrom pyvultr import VultrV2\n\n# Set your api key or we\'ll get it from env `VULTR_API_KEY`.\nVULTR_API_KEY = \'...\'\n\nv2 = VultrV2(api_key=VULTR_API_KEY)\n```\n\n#### Get Account\n```python\naccount = v2.account.get()\nprint(account)\n```\n\n#### List Region\n```python\nregions: VultrPagination[BackupItem] = v2.region.list()\n\n# Here `regions` is a VultrPagination object, you can use it like list, eg: get by index or slice.\n# VultrPagination will help you automatically get the next page when you need it.\n\nprint(regions[3:5])\n# >>> [RegionItem(id=\'dfw\', country=\'US\', options=[\'ddos_protection\'], continent=\'North America\', city=\'Dallas\'), RegionItem(id=\'ewr\', country=\'US\', options=[\'ddos_protection\', \'block_storage\'], continent=\'North America\', city=\'New Jersey\')]\n\nprint(regions[12])\n# >>> RegionItem(id=\'ord\', country=\'US\', options=[\'ddos_protection\'], continent=\'North America\', city=\'Chicago\')\n\n# Of course you can use `for` to iterate all items.\n# But be careful, it will cause a lot of requests if it\'s has a lot of data.\nfor region in regions:\n    print(region)\n\n# A smarter way to iterate is to determine the number of iterations you want.\nsmart_regions: VultrPagination[RegionItem] = v2.region.list(capacity=3)\nfor region in smart_regions:\n    print(region)\n# >>> RegionItem(id=\'ams\', country=\'NL\', options=[\'ddos_protection\'], continent=\'Europe\', city=\'Amsterdam\')\n# >>> RegionItem(id=\'atl\', country=\'US\', options=[\'ddos_protection\'], continent=\'North America\', city=\'Atlanta\')\n# >>> RegionItem(id=\'cdg\', country=\'FR\', options=[\'ddos_protection\'], continent=\'Europe\', city=\'Paris\')\n\n# At last, you can get all data just like calling attributes (better programming experience if you use IDE):\nfirst_region: RegionItem = regions.first()\nprint(first_region.country, first_region.city)\n# >>> NL Amsterdam\n```\n\n## CLI\nPyVultr also provides a command line interface.  \nIt\'s a simple wrapper of the python library using [Fire](https://github.com/google/python-fire),  and it has a beautiful output by using [Pygments](https://github.com/pygments/pygments).  \nIt registered a command `pyvultr` in the system, so you can just type `pyvultr` to use it:\n```shell\n# please setup Your API Key first:\n# you can generate your API Key from https://my.vultr.com/settings/#settingsapi\n# export VULTR_API_KEY="..."\n\n# show help by type `pyvultr`\n$ pyvultr\n```\n\n`pyvultr` cli usage is very similar to the python library usage.\nlet\'s explain this with get account information api :\n\n**In Python**:\n```python\nfrom pyvultr import VultrV2\n\n# here we get api key from env `VULTR_API_KEY`\nVultrV2().account.get()\n>>> AccountInfo(name=\'test man\', email=\'test@xxx.xxx\', acls=[\'manage_users\', \'subscriptions_view\', \'subscriptions\', \'billing\', \'support\', \'provisioning\', \'dns\', \'abuse\', \'upgrade\', \'firewall\', \'alerts\', \'objstore\', \'loadbalancer\', \'vke\'], balance=11.2, pending_charges=3.4, last_payment_date=\'2019-07-16T05:19:50+00:00\', last_payment_amount=-10)\n```\n\n**In CLI**:  \n```shell\n$ pyvultr account get\n{\n    "name": "test man",\n    "email": "test@xxx.xxx",\n    "acls": [\n        "manage_users",\n        "subscriptions_view",\n        "subscriptions",\n        "billing",\n        "support",\n        "provisioning",\n        "dns",\n        "abuse",\n        "upgrade",\n        "firewall",\n        "alerts",\n        "objstore",\n        "loadbalancer",\n        "vke"\n    ],\n    "balance": 11.2,\n    "pending_charges": 3.4,\n    "last_payment_date": "2019-07-16T05:19:50+00:00",\n    "last_payment_amount": -10\n}\n```\nActually, we have a beautiful output:  \n\n![CLI Example](./doc/cli_example.png)\n\n### Testing\n```Python\npython -m pytest -v\n```\n',
    'author': 'fishermanadg',
    'author_email': 'fishermanadg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/luxiaba/pyvultr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
