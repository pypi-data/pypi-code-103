# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['helpo']

package_data = \
{'': ['*']}

install_requires = \
['atlassian-python-api>=3.10.0,<4.0.0',
 'cloudflare>=2.8.15,<3.0.0',
 'hvac>=0.11.2,<0.12.0',
 'jsonmerge>=1.8.0,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'minio>=7.0.3,<8.0.0',
 'namecom>=0.5.0,<0.6.0',
 'packaging>=21.3,<22.0',
 'requests>=2.25.1,<3.0.0',
 'slumber>=0.7.1,<0.8.0',
 'tenacity>=8.0.1,<9.0.0',
 'typer>=0.4.0,<0.5.0',
 'zxpy>=1.2.2,<2.0.0']

entry_points = \
{'console_scripts': ['helpo = helpo.main:app']}

setup_kwargs = {
    'name': 'helpo',
    'version': '0.1.6',
    'description': 'Zadgroup helper cli scripts',
    'long_description': None,
    'author': 'Ahmed Kamel',
    'author_email': 'ahmedk@zadgroup.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
