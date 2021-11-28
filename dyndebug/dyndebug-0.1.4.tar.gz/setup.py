# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dyndebug']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'dyndebug',
    'version': '0.1.4',
    'description': 'A library to dynamically enable debug through configuration',
    'long_description': "# DynDebug - Dynamic Debug\n\nThis library provides the ability to dynamically enable or disable debug through environment configuration.\n\n## Usage\n\nUse the factory method to create a debug instance.  You provide a `context` value which is used to enable/disable debug through configuration.\n```\ndebug = Debug('MyContext1')\n```\n\nUse the debug instance to produce debug content\n```\ndebug('This is some debug')    \n```\n\nEnable the debug at run time by setting the DEBUG environment property to the list of contexts for which you want debug enabled.\n```\nexport DEBUG=MyContext1,MyContext2,...\n```",
    'author': 'aurecon',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
