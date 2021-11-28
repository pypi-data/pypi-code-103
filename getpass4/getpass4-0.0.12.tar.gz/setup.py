from setuptools import setup, find_packages
from os import path
import configparser

class Config(configparser.ConfigParser):
	def as_dict(self):
		d = dict(self._sections)
		for k in d:
			d[k] = dict(self._defaults, **d[k])
			d[k].pop('__name__', None)
		return d

config = Config()

config.read('setup.cfg')

dict = config.as_dict()

metadata = dict['metadata']
options = dict['options']

package_dir = {metadata['name']: metadata['name']}

rootdir = path.abspath(path.dirname(__file__))

long_description = open(path.join(rootdir, metadata['long_description_file'])).read()

LICENSE = ''

with open('LICENSE', 'r') as license_file:
	LICENSE = license_file.read()

setup(
	name=metadata['name'],
	python_requires=options['python_requires'],
	version=metadata['version'],
	author=metadata['author'],
	author_email=metadata['author_email'],
	description=metadata['description'],
	license=LICENSE,
	packages=find_packages(),
	install_requires=['caugetch', 'clipboard', 'colorama', 'pyperclip'],
)