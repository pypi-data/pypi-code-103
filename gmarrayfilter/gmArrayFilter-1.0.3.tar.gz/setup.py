#!/usr/bin/env python

from setuptools import setup, find_packages

version = "1.0.3"

msg = """------------------------------
Installing gmArrayFilter version {}
------------------------------
""".format(
    version
)
print(msg)

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name="gmArrayFilter",
    version=version,
    description="A python package to filter SNP array data",
    long_description=long_description,
    author="lx Gui",
    author_email="guilixuan@gmail.com",
    keywords=["bioinformatics", "NGS", "Reseq", "SNP"],
    url="https://gitee.com/brightrock/plant-gmap-array",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["array_plot.R", "params.cfg"]},
    scripts=["scripts/gmArray"],
    install_requires=["typer", "jinja2", "pandas", "cached_property", "delegator.py"],
    platforms=["all"],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)

msg = """------------------------------
gmArrayFilter installation complete!
------------------------------
"""
print(msg)
