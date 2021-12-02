# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['freelanceapi', 'freelanceapi.hwm', 'freelanceapi.msr', 'freelanceapi.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'freelanceapi',
    'version': '0.1.1',
    'description': 'FreelanceAPI is a module for reading & evaluating export files from the Freelance control system.',
    'long_description': 'FreecomAPI\n=======',
    'author': 'Peter Schwarz',
    'author_email': 'p.schwarz1994@outlook.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DarkJumper/FreelanceAPI',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9.1,<4.0.0',
}


setup(**setup_kwargs)
