import os
from setuptools import *

DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(DIR, "requirements.txt"), encoding = "utf-16") as file:
    REQUIREMENTS = file.readlines()

with open(os.path.join(DIR, "README.md"), encoding = "utf-8") as file:
    DESCRIPTION = file.read()

setup(
    name = "expdb",
    version = "1.0",
    author = "Devansh Singh",
    author_email = "devanshamity@gmail.com",
    url = "https://github.com/Devansh3712/expdb",
    description = "Python Library and CLI for exporting MySQL databases",
    long_description = DESCRIPTION,
    long_description_content_type = "text/markdown",
    license = "MIT",
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "expdb=expdb.cli:expdb"
        ]
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = REQUIREMENTS
)
