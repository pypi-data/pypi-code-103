"""
setup.py 

Information used to build the package
"""
from setuptools import find_namespace_packages, setup
import os
import subprocess


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


def get_version():
    ENV = os.environ['ENV'] # Must be set
    tag = subprocess.check_output(
        ['git', 'describe', '--tags', '--exact-match'],
        encoding='UTF-8'
    ).rstrip()
    if ENV in ['dev', 'test']:
        version = '0.' + tag
    elif ENV == 'prod':
        version = '1.' + tag
    else:
        raise ValueError(f"Unknown environment {ENV}")
    return version


setup(
    name="akerbp.models", 
    version=get_version(),
    author="Alfonso M. Canterla",
    author_email="alfonso.canterla@soprasteria.com",
    description="Machine Learning Models for Petrophysics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/akerbp/models/",
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "xgboost==1.3.3",
        "joblib==1.0.1",
        "numpy>=1.19.5",
        "pandas>=1.3.2",
        "scikit-learn>=0.24.2",
    ]
)