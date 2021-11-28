#!/usr/bin/env python
# setup.py generated by flit for tools that don't yet use PEP 517

from distutils.core import setup

packages = \
['i_xero2']

package_data = \
{'': ['*']}

install_requires = \
['aracnid-logger',
 'flask',
 'flask-oauthlib',
 'flask-session',
 'i-mongodb',
 'pytz',
 'xero-python']

setup(name='i_xero2',
      version='2.0.1',
      description='A set of functions to retrieve and save data into Xero.',
      author='Jason Romano',
      author_email='aracnid@gmail.com',
      url='https://github.com/aracnid/i-xero2',
      packages=packages,
      package_data=package_data,
      install_requires=install_requires,
      python_requires='~=3.9',
     )
