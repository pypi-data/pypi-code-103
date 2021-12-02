# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['auth_aws_profile']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.15,<2.0.0']

entry_points = \
{'console_scripts': ['auth-aws-profile = '
                     'auth_aws_profile.auth_aws_profile:main']}

setup_kwargs = {
    'name': 'auth-aws-profile',
    'version': '0.1.2',
    'description': 'Updates the configured MFA credentials for AWS services.',
    'long_description': None,
    'author': 'kdico',
    'author_email': '6wng7f78m@mozmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
