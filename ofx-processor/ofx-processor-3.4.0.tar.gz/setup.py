# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ofx_processor',
 'ofx_processor.downloaders',
 'ofx_processor.processors',
 'ofx_processor.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0',
 'dateparser>=1.1.0,<2.0.0',
 'ofxtools>=0.9.4,<0.10.0',
 'requests>=2.24.0,<3.0.0',
 'selenium>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['ynab = ofx_processor.main:cli']}

setup_kwargs = {
    'name': 'ofx-processor',
    'version': '3.4.0',
    'description': 'Personal ofx processor',
    'long_description': '# ofx-processor\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ofx-processor)\n![PyPI - Format](https://img.shields.io/pypi/format/ofx-processor)\n![PyPI - Status](https://img.shields.io/pypi/status/ofx-processor)\n\n## Install\n\n```shell\npython -m pip install ofx-processor\n```\n\nhttps://pypi.org/project/ofx-processor/\n\n## Usage\n\n```\nUsage: ynab [OPTIONS] COMMAND [ARGS]...\n\n  Import your data to YNAB with the processors listed below or manage your\n  config.\n\nOptions:\n  --version   Show the version and exit.\n  -h, --help  Show this message and exit.\n\nCommands:\n  config   Manage configuration.\n  bpvf     Import BPVF bank statement (OFX file).\n  ce       Import CE bank statement (OFX file).\n  lcl      Import LCL bank statement (OFX file).\n  revolut  Import Revolut bank statement (CSV file).\n```\n\nAll transactions will be pushed to YNAB. If this is your first time using the script,\nit will open a generated config file for you to fill up.\n\nThe account and budget UUID are found in the YNAB url when using the web app.\n\nThe file passed in parameter will be deleted unless specified (`--keep` option on each import command)\n\n## Versions\n\nThis project follows [Semantic Versioning](https://semver.org/).\n\n## Development\n### Release\n```shell\ninv full-test\npoetry version <major/minor/patch>\ngit add .\ngit commit\ninv tag <version>\ninv publish publish-docker\n```\n',
    'author': 'Gabriel Augendre',
    'author_email': 'gabriel@augendre.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.augendre.info/gaugendre/ofx-processor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
