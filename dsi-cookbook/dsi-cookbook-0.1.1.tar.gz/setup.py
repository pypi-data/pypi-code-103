# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsi_cookbook', 'dsi_cookbook.commands']

package_data = \
{'': ['*']}

install_requires = \
['typer-cli>=0.0.12,<0.0.13', 'typer>=0.3.0,<0.4.0']

entry_points = \
{'console_scripts': ['dsi-cookbook = dsi_cookbook.main:app']}

setup_kwargs = {
    'name': 'dsi-cookbook',
    'version': '0.1.1',
    'description': "The only cookbook you'll ever need",
    'long_description': "# `dsi-cookbook`\n\nThe only cookbook you'll ever need\n\n**Usage**:\n\n```console\n$ dsi-cookbook [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `ingredients`: manage ingredients\n* `recipes`: manage recipes\n\n## `dsi-cookbook ingredients`\n\nmanage ingredients\n\n**Usage**:\n\n```console\n$ dsi-cookbook ingredients [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `shop`\n\n### `dsi-cookbook ingredients shop`\n\n**Usage**:\n\n```console\n$ dsi-cookbook ingredients shop [OPTIONS]\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n\n## `dsi-cookbook recipes`\n\nmanage recipes\n\n**Usage**:\n\n```console\n$ dsi-cookbook recipes [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `ls`: list recipes\n\n### `dsi-cookbook recipes ls`\n\nlist recipes\n\n**Usage**:\n\n```console\n$ dsi-cookbook recipes ls [OPTIONS]\n```\n\n**Options**:\n\n* `--help`: Show this message and exit.\n",
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
