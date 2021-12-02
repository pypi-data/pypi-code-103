# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['axians_netbox_pdu',
 'axians_netbox_pdu.api',
 'axians_netbox_pdu.management',
 'axians_netbox_pdu.management.commands',
 'axians_netbox_pdu.migrations',
 'axians_netbox_pdu.tests']

package_data = \
{'': ['*'], 'axians_netbox_pdu': ['templates/axians_netbox_pdu/*']}

install_requires = \
['easysnmp>=0.2.5,<0.3.0',
 'invoke>=1.4.1,<2.0.0',
 'rq-scheduler>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'meraki-netbox-plugin-pdu',
    'version': '0.0.7',
    'description': 'A plugin for NetBox to easily display PDU information.',
    'long_description': '# Netbox PDU Plugin\n\nA plugin for [Netbox](https://github.com/netbox-community/netbox) to get power distribution unit Information.\n\n`axians-netbox-plugin-pdu` is using [Easy SNMP](https://easysnmp.readthedocs.io/en/latest/), [Django-RQ](https://github.com/rq/django-rq) and [RQ-Scheduler](https://github.com/rq/rq-scheduler) to display PDU information within Netbox.\n\n## Installation\nThe plugin is available as a Python package in pypi and can be installed with pip\n\n```\npip install axians-netbox-plugin-pdu\n```\n\n> The plugin is compatible with NetBox 2.9.1 and higher\n\nOnce installed, the plugin needs to be enabled in your `configuration.py`\n\n```python\nPLUGINS = ["axians_netbox_pdu"]\n\n# PLUGINS_CONFIG = {\n#   "axians_netbox_pdu": {\n#     ADD YOUR SETTINGS HERE\n#   }\n# }\n```\n\nThere are a number of default settings that can be altered using the following list of settings:\n\n* `schedule`: Boolean (default True). If True, this will enable automatic polling of your PDU Devices.\n* `schedule_interval`: Integer (default 300 seconds). Length of time between each scheduled poll.\n* `snmp_read`: String (default public) SNMP read value for your SNMP enabled PDU\'s.\n* `snmp_write`: String (default private) SNMP write value for your SNMP enabled PDU\'s.\n* `rack_view_pdu_devices`: Boolean (default True), if True, the power usage per PDU will be displayed on the rack page.\n* `rack_view_usage_summary`: Boolean (default True), if True, the a summary information tile will appear within the rack page to show true power utilization within the rack.\n* `rack_view_summary_unit`: String (default watts), option to display watts/kilowatts on the rack summary view. If "kilowatts" is used the power usage summary will display in Kilowatts.\n\n## Usage\n### Preparation\nFor this plugin to work there must be a new worker added to your Netbox installation. The new worker is a custom scheduler that will schedule the PDU Tasks to run on an interval and utilize the django-rq library.\n\n> You can utilize this library without the automated tasks by feeding Netbox the power usage information via the `axians_netbox_pdu` API.\n\n### Default Environment\nFor the standard install please use the included [netbox-pdu.service](contrib/netbox-pdu.service) and install using the standard [Netbox Documentation](https://netbox.readthedocs.io/en/stable/installation/migrating-to-systemd/).\n\n### Docker Environment\nTo use within Docker make sure you have a container running that runs the following command: `python manage.py pduschedule`\n\n### Adding a new PDU Configuration\nOnce installed and the `pduscheduler` is running you can attach a `PDUConfig` to a DeviceType. To do this you must have a DeviceType configured with PowerOutlets. You can specify the DeviceType, PDU SNMP OID and the Unit. This enables the plugin to know what SNMP OID to collect per DeviceType.\n\nNow a PDUConfig has been created a device must be created with a management IP. Once this is done the plugin can poll the PDU via SNMP and save the power usage.\n\nThis can also be done via Bulk Import or via the API.\n\n> If a a PDUConfig is not created for a DeviceType and the Device does not have a Primary IP no data will be collected.\n\n### API\nThe plugin includes several endpoints to manage the PDUConfig and PDUStatus.\n\n```\nGET       /api/plugins/pdu/pdu-config/         List PDUConfig\nPOST      /api/plugins/pdu/pdu-config/         Create PDUConfig\nPATCH/PUT /api/plugins/pdu/pdu-config/{id}/    Edit a specific PDUConfig\nDELETE /api/plugins/pdu/pdu-config/{id}/       Delete a specific PDUConfig\n\nGET       /api/plugins/pdu/pdu-status/         List PDUStatus\nPOST      /api/plugins/pdu/pdu-status/         Create PDUStatus\nPATCH/PUT /api/plugins/pdu/pdu-status/{id}/    Edit a specific PDUStatus\nDELETE /api/plugins/pdu/pdu-status/{id}/       Delete a specific PDUStatus\n```\n\n## Screen Shots\nList of PDUConfig Instances\n![PDUConfig List View](docs/images/PDUConfig_list.png)\n\nImport PDUConfig Instances\n![PDUConfig Import View](docs/images/PDUConfig_import.png)\n\nEdit PDUConfig Instances\n![PDUConfig Edit View](docs/images/PDUConfig_edit.png)\n\nView PDUStatus Device View\n![PDUStatus Device View](docs/images/PDUStatus_device.png)\n\nView PDUStatus Rack View\n![PDUStatus Rack View](docs/images/PDUStatus_rack.png)\n\n## Contributing\n\nPull requests are welcomed.\n\nThe project is packaged with a light development environment based on `docker-compose` to help with the local development of the project.\n\n- Black, Pylint, Bandit and pydockstyle for Python linting and formatting.\n- Django unit test to ensure the plugin is working properly.\n\n### CLI Helper Commands\n\nThe project comes with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.\n\nEach command can be executed with `invoke <command>`. All commands support the arguments `--netbox-ver` and `--python-ver` if you want to manually define the version of Python and Netbox to use. Each command also has its own help `invoke <command> --help`.\n\n#### Local dev environment\n```\n  build            Build all docker images.\n  debug            Start NetBox and its dependencies in debug mode.\n  destroy          Destroy all containers and volumes.\n  start            Start NetBox and its dependencies in detached mode.\n  stop             Stop NetBox and its dependencies.\n```\n\n\n#### Utility\n```\n  cli              Launch a bash shell inside the running NetBox container.\n  create-user      Create a new user in django (default: admin), will prompt for password.\n  makemigrations   Run Make Migration in Django.\n  nbshell          Launch a nbshell session.\n```\n#### Testing\n\n```\n  tests            Run all tests for this plugin.\n  pylint           Run pylint code analysis.\n  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.\n  bandit           Run bandit to validate basic static code security analysis.\n  black            Run black to check that Python files adhere to its style standards.\n  unittest         Run Django unit tests for the plugin.\n```',
    'author': 'Alex Houlton',
    'author_email': 'bob@meraki.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minitriga/axians-netbox-plugin-pdu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
