from setuptools import setup, find_packages
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
	long_description="""## How to use getpass4
```python
from getpass4 import getpass


password = getpass('Password: ')

print(password)
```""",
	packages=find_packages(),
	install_requires=['caugetch', 'clipboard', 'colorama', 'pyperclip'],
)