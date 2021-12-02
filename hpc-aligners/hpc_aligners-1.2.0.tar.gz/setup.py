#! /usr/bin/env python

"""
author: Nicolas JEANNE
email: jeanne.n@chu-toulouse.fr
Created on 22 jan. 2020
"""

import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hpc_aligners",
    version="1.2.0",
    author="Nicolas Jeanne",
    author_email="jeanne.n@chu-toulouse.fr",
    description="Using aligners in IUCT HPC solution. MAFFT and/or T-COFFEE must be in the path to be used (with conda environment for example).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://srvhpccode.icr.local/njeanne/python-package-hpc-aligner",
    packages=setuptools.find_packages(),
    classifiers=[
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research"],
    keywords="aligner hpc",
    license="GNU General Public License"
)
