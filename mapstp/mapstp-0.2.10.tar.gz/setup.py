# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mapstp', 'mapstp.cli', 'mapstp.utils']

package_data = \
{'': ['*'], 'mapstp': ['data/*']}

install_requires = \
['click-loguru>=1.3.7,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'tomli>=1.2.1,<2.0.0']

entry_points = \
{'console_scripts': ['mapstp = mapstp.cli.runner:mapstp']}

setup_kwargs = {
    'name': 'mapstp',
    'version': '0.2.10',
    'description': 'Transfers meta information from STP to MCNP',
    'long_description': '.. image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg\n   :target: https://github.com/MC-kit/map-stp/graphs/commit-activity\n\n.. image:: https://github.com/MC-kit/map-stp/workflows/Tests/badge.svg\n   :target: https://github.com/MC-kit/map-stp/actions?workflow=Tests\n   :alt: Tests\n\n.. image:: https://codecov.io/gh/MC-kit/map-stp/branch/master/graph/badge.svg?token=wlqoa368k8\n  :target: https://codecov.io/gh/MC-kit/map-stp\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n\n.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336\n    :target: https://pycqa.github.io/isort/\n\n\n.. image:: https://img.shields.io/github/license/MC-kit/map-stp\n   :target: https://github.com/MC-kit/map-stp\n\n.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n\n\nTransfer information from STP to MCNP\n-------------------------------------\n\nA user can add additional information on components directly to STP file component names with a special label.\nThe information may contain material, density correction factor, radiation waste checklist classification.\nThe package transfers this information to MCNP file (which is generated from this STP with SuperMC):\n\n    * sets materials and densities using information from STP labels and Excel material index file,\n    * adds $-comment after each cell denoting its path in STP, with tag "stp:",\n    * creates accompanying Excel file listing the MCNP cells and their properties: material, density, correction factor,\n      RWCL classification, STP path. This file can be used on MCNP results postprocessing.\n',
    'author': 'dvp',
    'author_email': 'dmitri_portnov@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MC-kit/map-stp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
