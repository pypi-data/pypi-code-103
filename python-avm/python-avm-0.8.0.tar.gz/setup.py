from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
	name='python-avm',
	version='0.8.0',
	license='MIT',
	description='An efficient variable manager tool.',
	author='Grosse-pasteque',
	author_email='grossepasteque.gamer34@gmail.com',
	url='https://github.com/Grosse-pasteque/AVM/',
	long_description=long_description,
	long_description_content_type='text/markdown',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		"Programming Language :: Python :: 3.10",
		'Programming Language :: Python :: 3 :: Only',
	],
	keywords=[
		'type-checking',
		'function-args-checking',
		'custom-types',
		'better-types',
		'function-args-convertion'
	],
	package_dir={'': 'src'},
	packages=find_packages(where='src'),
	python_requires='>=3.7, <4',
	install_requires=[
		# 'typing',
		# 'os',
		# 'abc',
		# 'inspect',
		# 'traceback',
	],
	project_urls={
		'Source': 'https://github.com/Grosse-pasteque/AVM/'
	}
)