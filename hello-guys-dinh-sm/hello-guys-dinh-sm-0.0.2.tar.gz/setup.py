import setuptools

with open("README.md", 'r') as fd:
	long_description = fd.read()

setuptools.setup(
	name = "hello-guys-dinh-sm",
	version = "0.0.2",
	author = "DINH Son-Michel",
	author_email = "son-michel.dinh@insa-lyon.fr",
	description = "Hands-on on software deployment, licenses, docstrings, doctests and sphinx documentation.",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://github.com/Dinh-SM/Package-Deployment-Test",
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent"
	],
	py_modules = ["hello_guys_dinh_sm"],
	package_dir = {"": "src"},
	packages = setuptools.find_packages(where="src"),
	python_requires = ">=3.7",
	install_requires = [
		"textblob",
		"googletrans==3.1.0a0"
	],
	license = "LICENSE"
)

# python3 setup.py sdist bdist_wheel
# python3 setup.py install