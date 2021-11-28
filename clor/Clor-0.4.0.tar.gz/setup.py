from setuptools import setup


setup(
  name         = 'Clor',
  version      = '0.4.0',
  author       = 'saaj',
  author_email = 'mail@saaj.me',
  license      = 'LGPL-2.1+',
  description  = 'Application configuration via Python logging.config',
  keywords     = 'python configuration-management',
  packages     = ['clor'],
  platforms    = ['Any'],
  url          = 'https://heptapod.host/saajns/clor',
  project_urls = {
    'Source Code'   : 'https://heptapod.host/saajns/clor',
    'Release Notes' : 'https://heptapod.host/saajns/clor/-/blob/branch/default/HISTORY.rst',
  },
  classifiers = [
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: Implementation :: CPython',
    'Intended Audience :: Developers',
  ],
  long_description = open('README.rst', 'rb').read().decode('utf-8'),
)
