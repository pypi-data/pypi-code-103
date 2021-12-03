# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pykeyatome']

package_data = \
{'': ['*']}

install_requires = \
['fake-useragent>=0.1.11,<0.2.0',
 'requests>=2.22.0,<3.0.0',
 'simplejson>=3.16.0,<4.0.0']

setup_kwargs = {
    'name': 'pykeyatome',
    'version': '1.1.2',
    'description': 'A simple API for key atome electricity consumption',
    'long_description': '# KeyAtome PyPi\n![GitHub release](https://img.shields.io/github/release/jugla/pyKeyAtome)\n\nGet your energy consumption data from Atome, a Linky-compatible device made by Total/Direct-Energie.\n\n### Installing\n```\npip install pykeyatome\n```\n\n## Use\nThe `__main__.py` is provided to show an example of use.\n\n3 types of function provided by client.py in `AtomeClient` class:\n- login : to be logged to the sever\n- get_live : to retrieve live statistics (instant power)\n- get_consumption(period) : to retrieve the consumption since a period (day/week/month/year)\n\n## Acknowledgments\n* Thanks to k20human for the original inspiration with https://github.com/k20human/domoticz-atome\n* Thanks to reverse engineering of Atome IOS APP performed by BaQs.\n* This project is a fork of https://github.com/BaQs/pyAtome (seems to be unmaintained)\n\n',
    'author': 'jugla',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jugla/pyKeyAtome',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.11',
}


setup(**setup_kwargs)
