#from distutils.core import setup
from setuptools import setup
from datetime import datetime
    
with open("README.md", "r",encoding="utf8") as fh:
    long_description = fh.read()
    
setup(
    # Application name:
    name="aesim.simba",

    # Version number:
    version="2021.12.02",

    # Application author details:
    author="AESIM.tech",
    author_email="contact@aesim.tech",
    
    # Packages
    packages=["aesim.simba"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://simba.io",

    license="By using aesim.simba, you agree to the license agreement available here: https://www.simba.io/static/EULA.pdf",
    
    description="Power Electronics and Motor Drive Simulation",

    long_description=long_description,
    long_description_content_type="text/markdown",

    # Dependent packages (distributions)
    install_requires=[
        "wheel",
        "pythonnet",
    ],
    
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    
    python_requires='>=3, !=3.9.*',
)
