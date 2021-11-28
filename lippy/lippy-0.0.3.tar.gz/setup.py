import setuptools
with open(r'D:\generate_my_pypi\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='lippy',
	version='0.0.3',
	author='Medvate',
	author_email='ilia.bezverzhenko@gmail.com',
	description='A module for solving linear programming problems.',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Medvate/lippy',
	packages=['lippy'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)