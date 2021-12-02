# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uberduckapi']

package_data = \
{'': ['*']}

install_requires = \
['polling>=0.3.2,<0.4.0', 'pydub>=0.25.0,<0.26.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'uberduckapi',
    'version': '0.1.18',
    'description': 'Python wrapper for uberduck API',
    'long_description': '# Python wrapper for the [UberDuck](https://uberduck.ai) API\nThis is a python wrapper for the uberduck api. You must have api access to use.\n\n# How this works?\nWell you first initialize a job by sending a request with your api key, secret, text, and voice name.\\\nAfter sending the request uberduck will issue a response with the status of the job.\nSo the api will poll this endpoint till a result is produced. the result is another url to the sound file that was created\n\nCheck the example.py for code\n\n',
    'author': 'George',
    'author_email': 'mazzeogeorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CupOfGeo/uberduckapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
