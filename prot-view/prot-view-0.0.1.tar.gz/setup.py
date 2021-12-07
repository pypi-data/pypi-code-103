#!/Library/Frameworks/Python.framework/Versions/3.9

from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="prot-view",
    version="0.0.1",
    description="Visualization tool to compare distributions of biochemical features"
    " for protein datasets.",
    py_modules=["ProtView"],
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # Add README to setup
    long_description=long_description,
    long_description_context_type="text/markdown",
    # Library Dependencies
    install_requires=[
        "biopython==1.79",
        "joblib==1.1.0",
        "numpy==1.21.4",
        "pandas==1.3.4",
        "patsy==0.5.1",
        "plotly==5.4.0",
        "progressbar==2.5",
        "PySimpleGUI==4.47.0",
        "python-dateutil==2.8.2",
        "pytz==2021.1",
        "scikit-learn==1.0.1",
        "scipy==1.7.3",
        "six==1.16.0",
        "sklearn==0.0",
        "statsmodels==0.10.2",
        "tenacity==8.0.1",
        "threadpoolctl==3.0.0",
    ],
    # Development Dependencies
    extras_require={
        "dev": [
            "pytest>=3.7",
        ],
    },
    url="https://github.com/michelle-an/ProtView",
    author="Michelle An",

)
