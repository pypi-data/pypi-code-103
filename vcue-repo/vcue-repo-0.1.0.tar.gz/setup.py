from setuptools import setup, find_packages 
from os import path 

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f: 
	long_description = f.read()

setup( 
	name='vcue-repo',
	version='0.1.0',
	description='basic functionality package for handling data',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/losDaniel/VCUErepo.git',
	author='Carlos Valcarcel',
	author_email='losdaniel@berkeley.edu',
	license='unlicensed',
	keywords='pandas data plotly scrape',
	packages=['vcue'],
	entry_points={
		'console_scripts':[
		]
	},
	install_requires=['pandas','numpy','bs4','matplotlib','plotly','sklearn','selenium'],
	package_data={
	},
	include_package_data=True,
)