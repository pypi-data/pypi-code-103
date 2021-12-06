# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dayu_widgets', 'dayu_widgets.qt', 'dayu_widgets.static']

package_data = \
{'': ['*']}

install_requires = \
['PySide2>=5.15.2,<6.0.0',
 'Qt.py>=1.3.6,<2.0.0',
 'dayu-path>=0.5.2,<0.6.0',
 'singledispatch>=3.7.0,<4.0.0',
 'six>=1.16.0,<2.0.0']

setup_kwargs = {
    'name': 'dayu-widgets',
    'version': '0.2.0',
    'description': 'UI components library for PySide',
    'long_description': None,
    'author': 'gandalfmu',
    'author_email': 'muyanru345@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/phenom-films/dayu_widgets',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
