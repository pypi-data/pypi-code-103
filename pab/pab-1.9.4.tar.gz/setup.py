# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbt',
 'pbt.package',
 'pbt.package.manager',
 'pbt.package.registry',
 'pbt.pipeline',
 'pbt.vcs']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'hugedict>=1.0.1',
 'lbry-rocksdb-optimized>=0.8.1,<0.9.0',
 'loguru>=0.5.3,<0.6.0',
 'networkx>=2.6.3,<3.0.0',
 'orjson>=3.6.3,<4.0.0',
 'poetry>=1.1.8,<2.0.0',
 'pytest-mock>=3.6.1,<4.0.0',
 'semver>=2.13.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'typing-extensions>=4.0.0,<5.0.0']

extras_require = \
{':python_version < "3.9"': ['graphlib_backport>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['pab = pbt.cli:cli', 'pbt = pbt.cli:cli']}

setup_kwargs = {
    'name': 'pab',
    'version': '1.9.4',
    'description': 'A build tool for poetry packages (living in submodules of a Git repo)',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
