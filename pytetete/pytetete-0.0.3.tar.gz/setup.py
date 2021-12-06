import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pytetete",
    version="0.0.3 ",
    description="Python library for news discourse analysis",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://pysophia2.readthedocs.io/en/latest/",
    author="Team Sophia2",
    author_email="sophia2.uach@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7"
    ],
    packages=["pysophia2"],
    install_requires=["pandas==1.2", "mariadb==1.0.6", "elasticsearch==7.13.3", "spacy==2.3.5", "matplotlib==3.3.4", "numpy==1.19.2"],

)