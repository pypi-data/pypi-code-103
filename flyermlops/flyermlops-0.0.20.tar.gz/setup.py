import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.rst").read_text()

# This call to setup() does all the work
setup(
    name="flyermlops",
    version="0.0.20",
    description="Helper package for deploying sagemaker pipelines on AWS and MLOPs",
    long_description="Helper functions for MLOps",
    long_description_content_type="text/x-rst",
    url="https://git.delta.com/ods/machine-learning/flyermlops",
    author="Steven Forrester",
    author_email="steven.forrester@delta.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "awswrangler>=2.10.0",
        "pandas>=1.1.5",
        "psycopg2-binary>=2.7.7",
        "SQLAlchemy>=1.4.23",
        "teradatasql>=17.10.0.2",
        "cookiecutter>=1.7.3",
        "PyYAML>=5.3.1",
        "boto3>=1.18.64",
        "sagemaker>=2.63.1",
        "scikit-learn>=0.24.0",
    ],
)
