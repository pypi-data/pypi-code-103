# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['csgoinvshuffle', 'csgoinvshuffle.enums']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.13,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'csgoinvshuffle',
    'version': '1.3.1',
    'description': 'A module for creating CS:GO inventory shuffle config files',
    'long_description': '# csgoinvshuffle\n[![PyPI version](https://badge.fury.io/py/csgoinvshuffle.svg)](https://badge.fury.io/py/csgoinvshuffle)\n[![GitHub license](https://img.shields.io/github/license/kreyoo/csgo-inv-shuffle)](https://github.com/kreyoo/csgo-inv-shuffle/blob/master/LICENSE)\n[![GitHub issues](https://img.shields.io/github/issues/kreyoo/csgo-inv-shuffle)](https://github.com/kreyoo/csgo-inv-shuffle/issues)\n![PyPI - Downloads](https://img.shields.io/pypi/dd/csgoinvshuffle)\n![Tests](https://github.com/kreyoo/csgo-inv-shuffle/actions/workflows/main.yml/badge.svg)\n# Description\n\ncsgoinvshuffle is a Python package designed to generate inventory shuffle config files for the game CS:GO.\n\nWith this package you can easily shuffle between different weapon types (e.g. M4A4 and M4A1-S) and have less limits in customizing the shuffle experience than with the in-game settings.\n\n## Note: \nCS:GO never really queues your items in a random order.\nThe items are arranged in one simple, predefined cycle.\nThis package aims to creating shuffles to your liking with ease\n\nYou can use the config file it creates and replace `<path_to_your_steam>/userdata/<your_steam_3id>/730/remote/cfg/csgo_saved_item_shuffles.txt` with it to apply your config.\n\n\n#### HINT: \nCS:GO needs to be closed while replacing the file\n\n\n\n\n\n# How to install\n\nThe package requires at least Python 3.9:\n```pip install csgoinvshuffle```\n\n# Basic usage\n\n## Your steam inventory needs to be public!\n### Basic shuffle for everything in your inventory with randomness\n\n```python\nfrom csgoinvshuffle import ShuffleConfig, get_inventory\n\nwith ShuffleConfig() as sc:\n    sc.add_items(get_inventory("YOUR_STEAM_ID_64"))\n    sc.randomize()\n```\n\n### Give items a certain order in the cycle\n```python\nfrom csgoinvshuffle import ShuffleConfig, get_inventory\nfrom csgoinvshuffle.enums import TagsInternalName\n\n# This example only works if you have at least 4 music kits in your inventory\nsc = ShuffleConfig()\ninv = get_inventory("YOUR_STEAM_ID_64")\nmusic_kits = inv.filter(TagsInternalName.MUSIC_KITS)\nsc.set_item(0 , music_kits[3])\nsc.set_item(1, music_kits[1])\nsc.save()\n```\n\nAs you can see in the last example, an inventory is equipped with a filter attribute and can be handled like a list.\nYou can filter for enums and the filter uses the TagsInternalName by default, as it is the most useful one.\nOtherwise using the built-in filter() function on the Inventory Object is suggested.\nTo get an overview of what values the attributes of an Item can have, you can lookup https://steamcommunity.com/inventory/<YOUR_STEAM_ID_64>/730/2 \nor lookup the typing definitions inside the item class.\nAs mentioned, typical values for the property `tags_internal_name` are provided by the TagsInternalName enum.\n\n\n### Create a shuffle cycle for only one team side\n\n```python\nfrom csgoinvshuffle import ShuffleConfig, get_inventory\nfrom csgoinvshuffle.enums import TagsInternalName, TeamSide\n\nwith ShuffleConfig() as sc:\n    inv = get_inventory("YOUR_STEAM_ID_64")\n    knives = inv.filter(TagsInternalName.KNIVES)\n    classic_knife = knives.filter(TagsInternalName.CLASSIC_KNIFE)[0]\n    karambit = knives.filter(TagsInternalName.KARAMBIT_KNIFE)[0]\n    butterfly = filter(lambda x: x.custom_name == "crypto is for n00bs", knives)[0]\n    # First map karambit, second map classic knife, third map butterfly, next map karambit again...\n    # On T side only\n    my_shuffle_cycle = [karambit, classic_knife, butterfly] \n    sc.add_items(my_shuffle_cycle, TeamSide.T)\n```\n\nBy default, the attribute methods from `ShuffleConfig` do everything for both teams.\nIf you want to have different shuffle cycles on the opposing sides, you have to state it with a parameter.\n\n',
    'author': 'Jan Vollmer',
    'author_email': 'zunder325@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kreyoo/csgo-inv-shuffle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
