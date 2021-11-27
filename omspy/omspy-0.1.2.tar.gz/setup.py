# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omspy', 'omspy.brokers', 'omspy.orders']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'pendulum>=2.1.2,<3.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'omspy',
    'version': '0.1.2',
    'description': '',
    'long_description': '# Omspy\n\nomspy is a broker agnostic order management system with a common api, advanced order types and more\n',
    'author': 'Ubermensch',
    'author_email': 'uberdeveloper001@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/uberdeveloper/omspy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
