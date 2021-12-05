from setuptools import setup

def read_requirements():
	with open('requirements.txt') as req:
		content = req.read()
		requirements = content.split('\n')
	return requirements

setup(
	name='aniinfo',
	version='0.4.5',
	packages=['aniinfo', 'aniinfo/data'],
	data_files=[('config', ['aniinfo/data/config.json'])],
	include_package_data=True,
	install_requires=read_requirements(),
	entry_points='''
		[console_scripts]
		aniinfo=aniinfo.main:help
	'''
)
