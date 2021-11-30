# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['secread', 'secread.tests']

package_data = \
{'': ['*'], 'secread.tests': ['data/*']}

install_requires = \
['python-dotenv>=0.18.0,<0.19.0',
 'requests>=2.26.0,<3.0.0',
 'types-requests>=2.25.9,<3.0.0']

setup_kwargs = {
    'name': 'secread',
    'version': '0.1.1',
    'description': 'This Python module allows to retrive secrets from Thycotic Secret Server. It utilizes the REST API',
    'long_description': None,
    'author': 'Josef Fuchs',
    'author_email': 'j053ff0x@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
