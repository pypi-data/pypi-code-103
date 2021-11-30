from setuptools import setup

# read the contents of README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'python-mydhl-api',         
  packages=['mydhl', 'mydhl.models', 'mydhl.constants', 'mydhl.cache', 'mydhl.endpoints'],
  version = '0.2.1',
  license='GPL-3.0-or-later',
  description = 'Wrapper for the MyDHL API (v2.5)',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Alexander Schillemans',
  author_email = 'alexander.schillemans@lhs.global',
  url = 'https://github.com/alexanderlhsglobal/python-mydhl-api',
  download_url = 'https://github.com/alexanderlhsglobal/python-mydhl-api/archive/refs/tags/0.2.1.tar.gz',
  keywords = ['mydhl', 'api', 'dhl express', 'dhl'],
  install_requires=[
          'requests',
          'python-dateutil',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3.6',
  ],
)