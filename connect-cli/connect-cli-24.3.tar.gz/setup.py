# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['connect',
 'connect..data.connect_reports.reports',
 'connect..data.connect_reports.reports.billing_requests',
 'connect..data.connect_reports.reports.billing_requests_line_item',
 'connect..data.connect_reports.reports.contract_list',
 'connect..data.connect_reports.reports.customers_list',
 'connect..data.connect_reports.reports.fulfillment_requests',
 'connect..data.connect_reports.reports.fulfillment_requests_failed',
 'connect..data.connect_reports.reports.fulfillment_requests_line_item',
 'connect..data.connect_reports.reports.listing_list',
 'connect..data.connect_reports.reports.listing_requests',
 'connect..data.connect_reports.reports.products_catalog',
 'connect..data.connect_reports.reports.sla',
 'connect..data.connect_reports.reports.subscription_list',
 'connect..data.connect_reports.reports.tier_configuration_list',
 'connect..data.connect_reports.reports.tier_configuration_requests',
 'connect..data.connect_reports.reports.usage_in_subscription',
 'connect.cli',
 'connect.cli.core',
 'connect.cli.core.account',
 'connect.cli.plugins',
 'connect.cli.plugins.customer',
 'connect.cli.plugins.play',
 'connect.cli.plugins.product',
 'connect.cli.plugins.product.sync',
 'connect.cli.plugins.project',
 'connect.cli.plugins.project.extension',
 'connect.cli.plugins.project.report',
 'connect.cli.plugins.report']

package_data = \
{'': ['*'],
 'connect': ['.data/connect_reports/*',
             '.data/connect_reports/.github/workflows/*'],
 'connect..data.connect_reports.reports.billing_requests': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.billing_requests_line_item': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.contract_list': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.customers_list': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.fulfillment_requests': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.fulfillment_requests_failed': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.fulfillment_requests_line_item': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.listing_list': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.listing_requests': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.products_catalog': ['templates/pdf/*',
                                                            'templates/pdf/assets/*',
                                                            'templates/pdf/img/*'],
 'connect..data.connect_reports.reports.sla': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.subscription_list': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.tier_configuration_list': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.tier_configuration_requests': ['templates/xlsx/*'],
 'connect..data.connect_reports.reports.usage_in_subscription': ['templates/xlsx/*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'connect-markdown-renderer>=1.0.1,<2.0.0',
 'connect-openapi-client>=24.0,<25.0',
 'connect-reports-core>=23.0.11,<24.0.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'fs>=2.4.12,<3.0.0',
 'interrogatio>=2.1.0,<3.0.0',
 'iso3166>=1.0.1,<2.0.0',
 'lxml>=4.6.2,<5.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'phonenumbers>=8.12.19,<9.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.25.1,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.59.0,<5.0.0']

entry_points = \
{'connect.cli.plugins': ['customer = '
                         'connect.cli.plugins.customer.commands:get_group',
                         'play = connect.cli.plugins.play.commands:get_group',
                         'product = '
                         'connect.cli.plugins.product.commands:get_group',
                         'project = '
                         'connect.cli.plugins.project.commands:get_group',
                         'report = '
                         'connect.cli.plugins.report.commands:get_group'],
 'console_scripts': ['ccli = connect.cli.ccli:main']}

setup_kwargs = {
    'name': 'connect-cli',
    'version': '24.3',
    'description': 'CloudBlue Connect Command Line Interface',
    'long_description': '# CloudBlue Connect Command Line Interface\n\n![pyversions](https://img.shields.io/pypi/pyversions/connect-cli.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-cli.svg)](https://pypi.org/project/connect-cli/) ![PyPI - Downloads](https://img.shields.io/pypi/dm/connect-cli) ![Docker Pulls](https://img.shields.io/docker/pulls/cloudblueconnect/connect-cli) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/cloudblue/connect-cli/Build%20Connect%20Command%20Line%20Client) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=coverage)](https://sonarcloud.io/summary/new_code?id=connect-cli) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-cli&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=connect-cli)\n\n## Introduction\n\nThe CloudBlue Connect Command Line Interface (CLI) is an extensible unified tool to perform various automation scenarios. With just one tool, you can control multiple Connect modules from the command line and automate them through scripts.\n\nSince it is extensible, users can write their own plugins to extend its functionalities.\n\n\n## Install\n\n### Prerequisites\n\n`connect-cli` depends on [Cairo](https://www.cairographics.org/), [Pango](https://pango.gnome.org/) and \n[GDK-PixBuf](https://developer.gnome.org/gdk-pixbuf/stable/).\n\nPlease refers to the platform-specific instructions on how to install these dependecies:\n\n* [Linux](docs/linux_deps_install.md)\n* [Mac OSX](docs/osx_deps_install.md)\n* [Windows](docs/win_deps_install.md)\n\n\n### Using PIP\n\nTo use `connect-cli` you need a system with python 3.8 or later installed.\n\n```sh\n    $ pip install --upgrade connect-cli\n```\n\n### Using Docker\n\nTo use the Docker image of `connect-cli`:\n\n```sh\n    $ docker run -it -v $HOME/.ccli:/home/connect/.ccli cloudblueconnect/connect-cli ccli\n```\n\nPlease refer to the [`connect-cli` docker image documentation](https://hub.docker.com/r/cloudblueconnect/connect-cli) for more information.\n\n\n### Using Homebrew (Mac OS X only)\n\nTo install `connect-cli` with homebrew run:\n\n```sh\n    $ brew update\n    $ brew tap cloudblue/connect\n    $ brew install cloudblue/connect/connect-cli\n```\n\n\n\n### Binary distributions\n\nA single executable binary distribution is available for windows, linux and mac os x.\nYou can it from the [Github Releases](https://github.com/cloudblue/connect-cli/releases) page.\n\nTo install under linux:\n\n```\n    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_linux_amd64.tar.gz\n    $ tar xvfz connect-cli_xx.yy_linux_amd64.tar.gz\n    $ sudo cp dist/ccli /usr/local/bin/ccli\n```\n\nTo install under Mac OS X:\n\n```\n    $ curl -O -J https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_osx_amd64.tar.gz\n    $ tar xvfz connect-cli_xx.yy_osx_amd64.tar.gz\n    $ sudo cp dist/ccli /usr/local/bin/ccli\n```\n\n> If your user is not a sudoer, you can copy the `ccli` executable from the dist directory to a directory of your choice\n> that is listed in the `PATH` variable.\n\n\nTo install under Windows\n\nDownload the windows single executable zipfile from [Github Releases](https://github.com/cloudblue/connect-cli/releases/download/xx.yy/connect-cli_xx.yy_windows_amd64.zip), extract it and place it in a folder that is included in your `PATH` system variable.\n\n\n## Usage\n\n* [General](docs/core_usage.md)\n* [Products](docs/products_usage.md)\n* [Customers](docs/customers_usage.md)\n* [Reports](docs/reports_usage.md)\n\n\n## Run tests\n\n`connect-cli` uses [poetry](https://python-poetry.org/) for dependencies management and packaging.\n\nTo run the `connect-cli` tests suite run:\n\n```\n$ pip install poetry\n$ poetry install\n$ poetry run pytest\n```\n\n\n## License\n\n`connect-cli` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).\n',
    'author': 'CloudBlue LLC',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://connect.cloudblue.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
