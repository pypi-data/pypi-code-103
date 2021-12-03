# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aws_org_inventory']
install_requires = \
['boto-collator-client>=0.1.1,<0.2.0',
 'boto3>=1.18.52,<2.0.0',
 'botocove>=1.3.1,<2.0.0',
 'pandas>=1.3.3,<2.0.0']

entry_points = \
{'console_scripts': ['aws-org-inventory = aws_org_inventory:main']}

setup_kwargs = {
    'name': 'aws-org-inventory',
    'version': '0.5.0',
    'description': " Dumps to CSV all the resources in an organization's member accounts",
    'long_description': None,
    'author': 'Iain Samuel McLean Elder',
    'author_email': 'iain@isme.es',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
