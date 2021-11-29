# -*- coding: utf-8 -*-

import os
import setuptools

EXCLUDE_FROM_PACKAGES = ["Output", "tests"]

with open("README.md", "r") as fh:
    long_description = fh.read()

# Load README.md for long description
def load_long_description(flname):
    if os.path.exists(flname):
        with open(flname, 'r') as f:
            long_description = f.read()
    else:
        long_description = 'Convert multiple file formats to other formats.'

    return long_description

def load_requirements(flname):
    try:
        # pip >= 10.0
        from pip._internal.req import parse_requirements        
    except:
        # pip < 10.0
        ImportError("pip needs to be updated.")

    reqs = parse_requirements(flname, session=False)
    try:
        requirements = [str(ir.requirement) for ir in reqs]
    except AttributeError:
        requirements = [str(ir.req) for ir in reqs]

    return requirements

setuptools.setup(
    name="flconverters",
    version="1.1.0",
    author = "Christos Synodinos",
    author_email = "chris_sinodinos@outlook.com",
    url="https://github.com/CSynodinos/converters",
    description = "Multiple file converters",
    long_description = load_long_description('README.md'),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=load_requirements("requirements.txt"),
    python_requires='>=3.6'
)