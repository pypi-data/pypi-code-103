# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datek_jaipur',
 'datek_jaipur.application',
 'datek_jaipur.application.adapters',
 'datek_jaipur.application.adapters.console',
 'datek_jaipur.application.state_machine',
 'datek_jaipur.domain',
 'datek_jaipur.domain.compound_types',
 'datek_jaipur.domain.errors',
 'datek_jaipur.domain.events']

package_data = \
{'': ['*']}

install_requires = \
['datek-async-fsm>=0.1.2,<0.2.0']

entry_points = \
{'console_scripts': ['run-console-app = datek_jaipur.application.console:main']}

setup_kwargs = {
    'name': 'datek-jaipur',
    'version': '0.1.0a1',
    'description': "Implementation of Jaipur board game's logic",
    'long_description': '# Jaipur board game\n\nThe game rules are implemented in *Domain Driven* -ish fashion.  \nA custom finite state machine is the driver and there is a console adapter available for it.\n\n### Usage \n\n- Run the game with `run-console-app`\n',
    'author': 'Attila Dudas',
    'author_email': 'dudasa7@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/DAtek/datek-jaipur',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
