#!/usr/bin/env python3

# https://packaging.python.org/tutorials/packaging-projects/
# https://packaging.python.org/guides/distributing-packages-using-setuptools/

import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="agunua", 
    version="1.6", # WARNING: if you modify it here, also change Agunua/__init__.py https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
    author="Stéphane Bortzmeyer",
    author_email="stephane+framagit@bortzmeyer.org",
    description="A library for the development of Gemini clients",
    keywords="Gemini",
    license="GPL",
    install_requires=['pyopenssl', 'PySocks', 'netaddr'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://framagit.org/bortzmeyer/agunua/",
    packages=["Agunua"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Intended Audience :: Developers",
        "Topic :: Internet",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    package_data={
        "Agunua": ["../sample-client.py", "../agunua.md", "../geminitrack.md", "../LICENSE", "../CHANGES"]
    },
    scripts=["geminitrack"],
    entry_points = {
        'console_scripts': ["agunua=Agunua.cli:main"]
    }
)
