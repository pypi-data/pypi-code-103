# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aerismodsdk', 'aerismodsdk.model', 'aerismodsdk.modules', 'aerismodsdk.utils']

package_data = \
{'': ['*']}

install_requires = \
['RPi.GPIO>=0.7.0,<0.8.0',
 'click>=7.0,<8.0',
 'cryptography>=3.0,<4.0',
 'pyjwt>=1.7.1,<2.0.0',
 'pyserial>=3.4,<4.0',
 'pyusb>=1.0.2,<2.0.0',
 'requests>=2.24.0,<3.0.0',
 'xmodem>=0.4.5,<0.5.0']

entry_points = \
{'console_scripts': ['aeriscli = aerismodsdk.cli:mycli']}

setup_kwargs = {
    'name': 'aerismodsdk',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
