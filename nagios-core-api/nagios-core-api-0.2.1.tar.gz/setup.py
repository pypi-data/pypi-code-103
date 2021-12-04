import pathlib
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="nagios-core-api",
    packages=find_packages(),
    version="0.2.1",
    license="MIT",
    description="A python wrapper for querying nagios core monitoring",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Sajal Shrestha",
    author_email="sajal.shres@gmail.com",
    url="https://github.com/sajalshres/nagios-core-api",
    keywords=["nagios", "api", "rest", "wrapper"],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
)
