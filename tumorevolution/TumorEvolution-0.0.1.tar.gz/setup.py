#!/usr/bin/env python3

import setuptools 

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="TumorEvolution",
	version="0.0.1",
	author="Nicolas Mendiboure",
	author_email="nicolas.mendiboure@insa-lyon.fr",
	description="Stochastic approach to compute tumor cells modelling",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/neonicoo/tumor-evolution-modeling",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	package_dir={'':'src'},
	packages=['tumorevolution'],
	#py_modules=["src/cell", "src/main", "src/tissue", "src/simulation"],
	python_requires = ">=3.6",
	install_requires = [
		"numpy",
		"pandas",
		"matplotlib",
	],
)

