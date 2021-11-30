# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qlacref_postcodes']

package_data = \
{'': ['*']}

install_requires = \
['rsa>=4.7.2,<5.0.0']

setup_kwargs = {
    'name': 'quality-lac-data-ref-postcodes',
    'version': '2021.8a5',
    'description': 'This is a redistribution of the ONS dataset on Lower Tier Local Authority toUpper Tier Local Authority Lookup packaged for the Quality Lac Data project.Source: Office for National Statistics licensed under the Open Government Licence v.3.0',
    'long_description': None,
    'author': 'Office for National Statistics',
    'author_email': 'sharedcustomercontactcentre@ons.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-postcodes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
