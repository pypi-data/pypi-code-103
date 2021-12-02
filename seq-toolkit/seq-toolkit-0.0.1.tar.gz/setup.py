from setuptools import setup
import re
import os
import sys


setup(
    name="seq-toolkit",
    version="0.0.1",
    python_requires=">3.7.0",
    author="Michael E. Vinyard - Harvard University - Massachussetts General Hospital - Broad Institute of MIT and Harvard",
    author_email="mvinyard@broadinstitute.org",
    url=None,
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    description="seq-toolkit - Basic sequence manipulation tools. A vintools package.",
    packages=[
        "seq-toolkit",
    ],
    
    install_requires=[
	"licorice>=0.0.2",
	"vinplots>=0.0.1",
	"pandas>=1.3.3",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    license="MIT",
)
