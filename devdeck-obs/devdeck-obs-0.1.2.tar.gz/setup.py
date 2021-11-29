# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['devdeck_obs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'devdeck-obs',
    'version': '0.1.2',
    'description': 'OBS support for DevDeck',
    'long_description': '# DevDeck - OBS\n\nOBS controls for [DevDeck](https://github.com/jamesridgway/devdeck).\n\nIn this example, you can change scenes in OBS.\n\n\n## Installing\nSimplify install *DevDeck - OBS* into the same python environment that you have installed DevDeck.\n\n    pip install devdeck-obs\n\nYou can then update your DevDeck configuration to use decks and controls from this package.\n\n## Configuration\n\nExample configuration:\n```yaml\ndecks:\n  - serial_number: "ABC123"\n    name: \'devdeck.decks.single_page_deck_controller.SinglePageDeckController\'\n    settings:\n      controls:\n        - key: 3\n          name: devdeck_obs.obs_control.OBSControl\n          settings:\n            scene_name: Webcam\n            emoji: \'camera\'\n        - key: 8\n          name: devdeck_obs.obs_control.OBSControl\n          settings:\n            scene_name: Desktop\n            emoji: \'desktop_computer\'\n        - key: 13\n          name: devdeck_obs.obs_control.OBSControl\n          settings:\n            scene_name: AFK\n            emoji: \'zzz\'\n```\n\n\n\n## Credentials\nCurrently this does not use a username and password to access the OBS websocket. This may change in future, but the default will always be `\'\':\'\'`.\n',
    'author': 'Tom Whitwell',
    'author_email': 'tom@whi.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
