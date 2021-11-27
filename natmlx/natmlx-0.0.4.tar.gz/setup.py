#
#   NatMLX
#   Copyright (c) 2021 Yusuf Olokoba.
#

from os import path, walk
from setuptools import find_packages, setup

# Get readme
with open("README.md", "r") as readme:
    long_description = readme.read()

# Get version
with open("natmlx/version.py") as version_source:
    gvars = {}
    exec(version_source.read(), gvars)
    version = gvars["__version__"]

# Load template data
def package_files(directory):
    paths = []
    for file_path, _, filenames in walk(directory):
        for filename in filenames:
            paths.append(path.join("..", file_path, filename))
    return paths
template_data = package_files("natmlx/templates")

# Setup
setup(
    name="natmlx",
    version=version,
    author="NatML",
    author_email="hi@natml.ai",
    description="Machine learning extensions for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
	python_requires=">=3.6",
    install_requires=[
        "path",
        "pyyaml"
    ],
    url="https://github.com/natsuite/NatMLX-Py",
    packages=find_packages(include=["natmlx", "natmlx.*"]),
    package_data={
        "": template_data
    },
    entry_points={
        "console_scripts": [
            "natml-template=natmlx.template:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://docs.natml.ai/python",
        "Source": "https://github.com/natsuite/NatMLX-Py"
    },
)