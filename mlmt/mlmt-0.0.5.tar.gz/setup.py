# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlmt']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.0,<2.0.0', 'pandas>=1.0,<2.0']

setup_kwargs = {
    'name': 'mlmt',
    'version': '0.0.5',
    'description': 'A Machine Learning Multi-Tool',
    'long_description': "# A Machine Learning Multi-Tool (mlmt)\n\n[![Downloads per month badge](https://pepy.tech/badge/mlmt/month)](https://pepy.tech/project/mlmt)\n[![Link to project on pypi badge](https://img.shields.io/pypi/v/mlmt)](https://pypi.org/project/mlmt/)\n[![Package format badge](https://img.shields.io/pypi/format/mlmt)](https://pypi.org/project/mlmt/)\n[![Supported python versions badge](https://img.shields.io/pypi/pyversions/mlmt)](https://pypi.org/project/mlmt/)\n[![License badge](https://img.shields.io/pypi/l/mlmt)](https://pypi.org/project/mlmt/)\n[![Documentation Status](https://readthedocs.org/projects/mlmt/badge/?version=latest)](https://mlmt.readthedocs.io/en/latest/?badge=latest)\n\nA collection of loosely organized code to assist machine learning research.\n\nmlmt @ [GitHub](https://github.com/rlan/mlmt), [PyPi](https://pypi.org/project/mlmt) and [ReadTheDocs](https://mlmt.readthedocs.io/en/latest/?badge=latest).\n\n## Installation\n\n```sh\npip install --upgrade mlmt\n```\n\n## Usage\n\n```python\nimport mlmt\n```\n\n## Developer's Guide\n\nSee project [wiki](https://github.com/rlan/mlmt/wiki).\n",
    'author': 'Rick Lan',
    'author_email': 'rlan@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rlan/mlmt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
