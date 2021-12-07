# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyipasnhistory']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=4.2.0,<5.0.0']}

entry_points = \
{'console_scripts': ['ipasnhistory = pyipasnhistory:main']}

setup_kwargs = {
    'name': 'pyipasnhistory',
    'version': '2.1',
    'description': 'Python client for IP ASN History',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/pyipasnhistory/badge/?version=latest)](https://pyipasnhistory.readthedocs.io/en/latest/)\n\n# PyIPASNHistory\n\nThis is the client API for [IP ASN History](https://github.com/D4-project/IPASN-History).\n\n## Installation\n\n```bash\npip install pyipasnhistory\n```\n\n## Usage\n\n### Command line\n\nYou can use the `ipasnhistory` command to query the instance.\n\n```bash\nusage: ipasnhistory [-h] [--url URL] (--meta | --file FILE | --ip IP) [--source SOURCE] [--address_family ADDRESS_FAMILY] [--date DATE] [--first FIRST]\n                    [--last LAST]\n\nRun a query against IP ASN History\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --url URL             URL of the instance.\n  --meta                Get meta information.\n  --file FILE           Mass process queries from a file.\n  --ip IP               IP to lookup\n  --source SOURCE       Source to query (currently, only "caida" and "ripe_rrc00" are supported)\n  --address_family ADDRESS_FAMILY\n                        Can be either v4 or v6\n  --date DATE           Exact date to lookup. Fallback to most recent available.\n  --first FIRST         First date in the interval\n  --last LAST           Last date in the interval\n```\n\n### Library\n\nSee [API Reference](https://pyipasnhistory.readthedocs.io/en/latest/api_reference.html)\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lookyloo/PyLookyloo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
