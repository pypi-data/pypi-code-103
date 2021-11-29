import os
from setuptools import setup, find_packages


def get_version():
    project_dir = os.path.abspath(os.path.dirname(__file__))
    version_filename = os.path.join(project_dir, "artefacts", "VERSION")
    version = open(version_filename).read().strip()
    return version


setup(
    name="artefacts",
    version=get_version(),
    description="Utilities for building on dbt artifacts",
    long_description="Please see the documentation site "
    "https://github.com/tjwaterman99/artefacts",
    author="Tom Waterman",
    license="Apache License 2.0",
    author_email="tjwaterman99@gmail.com",
    url="https://github.com/tjwaterman99/artefacts",
    packages=find_packages(),
    install_requires=[
        "pydantic==1.8.2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
    package_data={"": ["VERSION"]},
)
