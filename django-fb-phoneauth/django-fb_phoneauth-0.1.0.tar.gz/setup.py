# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fb_phoneauth', 'fb_phoneauth.migrations']

package_data = \
{'': ['*'],
 'fb_phoneauth': ['static/fb_phoneauth/*',
                  'templates/fb_phoneauth/*',
                  'templates/fb_phoneauth/partials/*']}

install_requires = \
['Django>=3.1,<4.0',
 'django-phonenumber-field>5.0.0',
 'firebase-admin>=5.1.0,<6.0.0',
 'phonenumbers>=8.12.38,<9.0.0']

setup_kwargs = {
    'name': 'django-fb-phoneauth',
    'version': '0.1.0',
    'description': 'Google Firebase authentication for django applications.',
    'long_description': None,
    'author': 'prajeeshag',
    'author_email': 'prajeeshag@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
