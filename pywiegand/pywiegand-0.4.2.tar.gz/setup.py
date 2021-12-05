# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywiegand']

package_data = \
{'': ['*'],
 'pywiegand': ['extension/pywiegand_adapter.cpp',
               'extension/pywiegand_adapter.cpp',
               'extension/pywiegand_adapter.h',
               'extension/pywiegand_adapter.h']}

install_requires = \
['wiringPi']

setup_kwargs = {
    'name': 'pywiegand',
    'version': '0.4.2',
    'description': 'Wiegand protocol on Raspberry PI',
    'long_description': "# Python Wiegand reader on Raspberry PI\n\nUsing GPIO you can read the key presses and card codes from a keypad with the Wiegand protocol.\n\n```python\n>>> from  pywiegand import WiegandReader\n>>> wr = WiegandReader(6, 5)\n# reading card\n>>> wr.read()\n'560019750914'\n\n# reading keys\n>>> wr.read()\n['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '#']\n```\n",
    'author': 'Gábor Kovács',
    'author_email': 'gkovacs81@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ArPIHomeSecurity/pywiegand',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
