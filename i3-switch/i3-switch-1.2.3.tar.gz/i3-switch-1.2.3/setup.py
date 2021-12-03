from setuptools import setup
from os import path

version = '1.2.3'

repo_base_dir = path.abspath(path.dirname(__file__))

# Long description
readme = path.join(repo_base_dir, 'README.md')
with open(readme) as f:
	long_description = f.read()

setup(
	name='i3-switch',
	version=version,
	description='i3 script to switch between windows in history',
	long_description_content_type='text/markdown',
	long_description=long_description,
	author='DCsunset',
	license='MIT',
	url='https://github.com/DCsunset/i3-switch',

	install_requires=['i3ipc'],
	# Add to lib so that it can be included
	scripts=["i3-switch"],

	classifiers=[
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'Programming Language :: Python',
		'License :: OSI Approved :: MIT License'
	]
)
