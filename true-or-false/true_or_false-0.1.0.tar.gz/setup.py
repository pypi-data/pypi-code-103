# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['true_or_false']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'true-or-false',
    'version': '0.1.0',
    'description': 'A simple python module to determine whether an input is True or False.',
    'long_description': "# true_or_false\nA simple python funciton to determine whether an input is True or False\n\nDetermine (educated guess) whether an input value is True\nor False.  Input can be a bool, dict, int or str.  This is\nuseful for determining the value of a parameter as passed\nin via environment variable, cli, config file or plain\npython code.\n\nExamples of True values:\n  str: ['true', 't', '1', 'yes', 'y', 't', 'oui']\n  bool: True\n  dict: {'a': 1} # any non empty dictionary\n  list: [0]  # any list not zero length\n\nExamples of False values:\n  str FALSES = ['false', 'f', '0', 'no', 'n', 'non']\n  bool: False\n  dict: {}  # empty dictionary\n  list: []  # empty list\n\n## Installation\n\n  pip install true-or-false\n\n## Usage\n\n```\nfrom true_or_false import true_or_false\n\nb = true_or_false(1)\nprint(b)\n>> True\n```",
    'author': 'Albert Pang',
    'author_email': 'alpaalpa@mac.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alpaalpa/true_or_false',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
