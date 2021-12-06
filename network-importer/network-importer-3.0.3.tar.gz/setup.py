# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['network_importer',
 'network_importer.adapters',
 'network_importer.adapters.nautobot_api',
 'network_importer.adapters.netbox_api',
 'network_importer.adapters.network_importer',
 'network_importer.drivers',
 'network_importer.processors']

package_data = \
{'': ['*'], 'network_importer': ['templates/*']}

install_requires = \
['click>=7.1,<8.0',
 'diffsync>=1.2,<2.0',
 'genie>=21.4.0,<21.5.0',
 'netmiko>=3.3,<4.0',
 'nornir-napalm>=0.1.2,<0.2.0',
 'nornir-netmiko>=0.1.1,<0.2.0',
 'nornir-utils>=0.1.2,<0.2.0',
 'nornir>=3.0,<4.0',
 'ntc-templates>=2.0,<3.0',
 'pyats>=21.4.0,<21.5.0',
 'pybatfish==2021.2.26.830',
 'pydantic>=1.6,<2.0',
 'pynautobot>=1.0.2,<2.0.0',
 'pynetbox>=5.0,<6.0',
 'rich>=9.2,<10.0',
 'structlog>=20.1.0,<21.0.0',
 'termcolor>=1.1,<2.0',
 'toml>=0.10,<0.11']

entry_points = \
{'console_scripts': ['network-importer = network_importer.cli:main']}

setup_kwargs = {
    'name': 'network-importer',
    'version': '3.0.3',
    'description': 'Network Importer tool to import an existing network into a Database / Source Of Truth',
    'long_description': "# Network Importer\n\nThe network importer is a tool/library to analyze and/or synchronize an existing network with a Network Source of Truth (SOT), it's designed to be idempotent and by default it's only showing the difference between the running network and the remote SOT. \n\nThe main use cases for the network importer: \n - Import an existing network into a SOT (Netbox) as a first step to automate a brownfield network\n - Check the differences between the running network and the Source of Truth\n\n## Quick Start\n\n- [Getting Started](docs/getting_started.md)\n- [Configuration file](docs/configuration.md)\n- [Supported Features and Architecture](docs/architecture.md)\n- [Extensibility](docs/extensibility.md)\n- [Upgrade procedure](docs/upgrade.md)\n\n## Questions\n\nFor any questions or comments, please feel free to open an issue or swing by the [networktocode slack channel](https://networktocode.slack.com/). (channel #networktocode)\n\nSign up [here](http://slack.networktocode.com/)",
    'author': 'Network to Code, LLC',
    'author_email': 'opensource@networktocode.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/networktocode/network-importer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
