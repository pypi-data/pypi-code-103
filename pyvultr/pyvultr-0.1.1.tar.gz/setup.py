# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyvultr', 'pyvultr.utils', 'pyvultr.v2']

package_data = \
{'': ['*']}

install_requires = \
['dacite>=1.6.0,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'pyvultr',
    'version': '0.1.1',
    'description': 'Python library for Vultr API',
    'long_description': "## Python Library for [Vultr](https://www.vultr.com/) API\n\nThe unofficial python library for the Vultr API in python.\n\n[![CI](https://github.com/luxiaba/pyvultr/actions/workflows/ci.yaml/badge.svg)](https://github.com/luxiaba/pyvultr/actions/workflows/ci.yaml)\n![PyPI](https://img.shields.io/pypi/v/pyvultr?color=blue&label=PyPI)\n\n[![Python 3.6.8](https://img.shields.io/badge/python-3.6.8-blue.svg)](https://www.python.org/downloads/release/python-368/)\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n\n### Installation\n```\npip install -U pyvultr\n```\n\n### Usage\n\n#### Configuration\n```python\nfrom pyvultr import VultrV2\n\n# set your api key or we'll get it from env `VULTR_API_KEY`\nVULTR_API_KEY = '...'\n\nv2 = VultrV2(api_key=VULTR_API_KEY)\n```\n\n#### Get Account\n```python\naccount = v2.account.get()\nprint(account)\n```\n\n#### List Region\n```python\nregions: VultrPagination[BackupItem] = v2.region.list()\n\n# Here `regions` is a VultrPagination object, you can use it like list, eg: get by index or slice.\n# VultrPagination will help you automatically get the next page when you need it.\n\nprint(regions[3:5])\n# >>> [RegionItem(id='dfw', country='US', options=['ddos_protection'], continent='North America', city='Dallas'), RegionItem(id='ewr', country='US', options=['ddos_protection', 'block_storage'], continent='North America', city='New Jersey')]\n\nprint(regions[12])\n# >>> RegionItem(id='ord', country='US', options=['ddos_protection'], continent='North America', city='Chicago')\n\n# Of course you can use `for` to iterate all items, but be careful,\n# it will cause a lot of requests if it's has a lot of data.\nfor region in regions:\n    print(region)\n\n# A smarter way to iterate is to determine the number of iterations you want.\nsmart_regions: VultrPagination[RegionItem] = v2.region.list(capacity=3)\nfor region in smart_regions:\n    print(region)\n# >>> RegionItem(id='ams', country='NL', options=['ddos_protection'], continent='Europe', city='Amsterdam')\n# >>> RegionItem(id='atl', country='US', options=['ddos_protection'], continent='North America', city='Atlanta')\n# >>> RegionItem(id='cdg', country='FR', options=['ddos_protection'], continent='Europe', city='Paris')\n\n# At last, you can get all data just like calling attributes (better programming experience if you use IDE):\nfirst_region: RegionItem = regions.first()\nprint(first_region.country, first_region.city)\n# >>> NL Amsterdam\n```\n\n### Testing\n```Python\npython -m pytest -v\n```\n",
    'author': 'fishermanadg',
    'author_email': 'fishermanadg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/luxiaba/pyvultr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
