# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyhashlookup']

package_data = \
{'': ['*']}

install_requires = \
['dnspython>=2.1.0,<3.0.0', 'requests>=2.26.0,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=4.3.1,<5.0.0']}

entry_points = \
{'console_scripts': ['hashlookup = pyhashlookup:main']}

setup_kwargs = {
    'name': 'pyhashlookup',
    'version': '1.1',
    'description': 'Python CLI and module for CIRCL hash lookup',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/pyhashlookup/badge/?version=latest)](https://pyhashlookup.readthedocs.io/en/latest/?badge=latest)\n\n# PyHashlookup\n\nThis is the client API for [hashlookup](https://hashlookup.circl.lu/).\n\n## Installation\n\n```bash\npip install pyhashlookup\n```\n\n## Usage\n\n### Command line\n\n```bash\nusage: hashlookup [-h] [--query QUERY]\n\nQuery hashlookup\n\noptional arguments:\n  -h, --help     show this help message and exit\n    --query QUERY  Hash (md5 or sha1) to lookup.\n```\n\n### Library\n\nSee [API Reference](https://pyhashlookup.readthedocs.io/en/latest/api_reference.html)\n',
    'author': 'Raphaël Vinot',
    'author_email': 'raphael.vinot@circl.lu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CIRCL/PyHashlookup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
