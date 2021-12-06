# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cryptoco_py']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['cryptoco-py = cryptoco_py.__main__:app']}

setup_kwargs = {
    'name': 'cryptoco-py',
    'version': '0.1.4',
    'description': 'A package to query cryptocurrency information',
    'long_description': '',
    'author': 'Jawad Abduljawad(TerminalJ)',
    'author_email': 'jawadhamdiabduljawad@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
