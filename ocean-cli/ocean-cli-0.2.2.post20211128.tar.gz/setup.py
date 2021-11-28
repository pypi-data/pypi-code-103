import os
from setuptools import setup, find_packages

from ocean.code import VERSION


setup_requires = ["setuptools", "wheel", "twine"]

install_requires = [
    "click~=8.0.1",
    "python-dateutil",
    "requests~=2.26.0",
    "inquirer",
    "pyyaml",
    "sentry-sdk",
]

dependency_links = []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ocean-cli",
    version=VERSION,
    description="Ocean CLI",
    url="https://github.com/AI-Ocean/ocean-cli",
    author="kairos03",
    author_email="kairos0=9603@email.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    entry_points={"console_scripts": ["ocean = ocean.main:cli"]},
    zip_safe=False,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
