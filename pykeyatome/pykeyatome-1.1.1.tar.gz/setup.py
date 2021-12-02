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
    'version': '1.1.1',
    'description': 'A simple API for key atome electricity consumption',
    'long_description': "# KeyAtome PyPi\n![GitHub release](https://img.shields.io/github/release/jugla/pyKeyAtome)\n\nGet your energy consumption data from Atome, a Linky-compatible device made by Total/Direct-Energie.\n\n### Installing\n\n```\npip install pykeyatome\n```\n\n\n## Running the tests\nThe tox configuration is already included.\nSimply launch:\n```\n$ tox\n```\n\n(Do not forget to 'pip install tox' if you do not have it.)\nTests are written in the tests directory.\ntests/data folder contains samples of Atome API for tests purposes.\n\n\n## Side notes\n\nThis project is based on reverse engineering of Atome IOS APP performed by BaQs.\n\n\n## Contributing\n\nAny contribution is welcome, considering the number of features the API provides, there is room for improvement!\n\n## Acknowledgments\n\n* Thanks to k20human for the original inspiration with https://github.com/k20human/domoticz-atome\n* This project is a fork of https://github.com/BaQs/pyAtome (seems to be unmaintained)\n\n## Changelog\n\n### 1.0.0 first release\n",
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
