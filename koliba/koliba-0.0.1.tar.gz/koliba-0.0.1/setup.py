from setuptools import *

module1 = Extension('koliba', libraries=['koliba'], sources=['kolibamodule.c'])

setup (name = 'koliba',
version = '0.0.1',
author = 'G. Adam Stanislav',
description = 'A Python port of the koliba library',
long_description = 'file: README.md',
long_description_content_type = 'text/markdown',
url = 'https://github.com/Pantarheon/koliba',
classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: BSD License",
	"Operating System :: OS Independent",
],
ext_modules = [module1])
