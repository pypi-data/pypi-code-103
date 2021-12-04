# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['roonapi']

package_data = \
{'': ['*']}

install_requires = \
['ifaddr>=0.1.0', 'requests>=2.0', 'six>=1.10.0', 'websocket_client>=0.57.0']

setup_kwargs = {
    'name': 'roonapi',
    'version': '0.0.39',
    'description': 'Provides a python interface to interact with Roon',
    'long_description': '# pyRoon ![Build status](https://github.com/pavoni/pyroon/workflows/Build/badge.svg) ![PyPi version](https://img.shields.io/pypi/v/roonapi) ![PyPi downloads](https://img.shields.io/pypi/dm/roonapi)\npython library to interface with the Roon API (www.roonlabs.com)\n\nSee https://github.com/pavoni/pyroon/tree/master/examples for code examples.\n\n\nAn example of connecting to the roon server and using a subscription:\n\n```\nimport time\n\nfrom roonapi import RoonApi\n\nappinfo = {\n    "extension_id": "python_roon_test",\n    "display_name": "Python library for Roon",\n    "display_version": "1.0.0",\n    "publisher": "gregd",\n    "email": "mygreat@emailaddress.com",\n}\n\n# Can be None if you don\'t yet have a token\ntoken = open("mytokenfile").read()\n\n# Take a look at examples/discovery if you want to use discovery.\nserver = "192.168.1.160"\n\nroonapi = RoonApi(appinfo, token, server)\n\n\ndef my_state_callback(event, changed_ids):\n    """Call when something changes in roon."""\n    print("my_state_callback event:%s changed_ids: %s" % (event, changed_ids))\n    for zone_id in changed_ids:\n        zone = roonapi.zones[zone_id]\n        print("zone_id:%s zone_info: %s" % (zone_id, zone))\n\n\n# receive state updates in your callback\nroonapi.register_state_callback(my_state_callback)\n\ntime.sleep(60)\n\n# save the token for next time\nwith open("mytokenfile", "w") as f:\n    f.write(roonapi.token)```\n',
    'author': 'Marcel van der Veldt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pavoni/pyroon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
