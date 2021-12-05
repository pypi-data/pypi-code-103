# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsi_cookbook', 'dsi_cookbook.commands']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['dsi-cookbook = dsi_cookbook.main:app']}

setup_kwargs = {
    'name': 'dsi-cookbook',
    'version': '0.1.0',
    'description': '',
    'long_description': '# `dsirecipes`\n\nAwesome Portal Gun\n\n**Usage**:\n\n```console\n$ dsirecipes [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `load`: Load the portal gun\n* `shoot`: Shoot the portal gun\n\n## `dsirecipes load`\n\nLoad the portal gun\n\n**Usage**:\n\n```console\n$ dsirecipes load [OPTIONS]\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n\n## `dsirecipes shoot`\n\nShoot the portal gun\n\n**Usage**:\n\n```console\n$ dsirecipes shoot [OPTIONS]\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n',
    'author': 'Qiushi Yan',
    'author_email': 'qiushi.yann@gmail.com',
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
