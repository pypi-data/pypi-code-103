# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['munet']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0']

extras_require = \
{'ide': ['Pygments>=2.10.0,<3.0.0',
         'autoflake>=1.4,<2.0',
         'flake8>=3.9.2,<4.0.0',
         'importmagic>=0.1.7,<0.2.0',
         'jedi>=0.18.0,<0.19.0',
         'json-rpc>=1.13.0,<2.0.0']}

entry_points = \
{'console_scripts': ['munet = munet.__main__:main']}

setup_kwargs = {
    'name': 'munet',
    'version': '0.3.1',
    'description': 'A package to facilitate network simulations',
    'long_description': '# μNET (munet)\n\nA package for creating network topologies and running programs and containers\nwithin them using linux namepsaces.\n',
    'author': 'Christian Hopps',
    'author_email': 'chopps@labn.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LabNConsulting/munet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
