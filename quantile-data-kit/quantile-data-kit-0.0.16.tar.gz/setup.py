from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

default_packages = [
    "pandas==1.3.3",
    "dagster==0.13.0",
    "mlflow==1.20.2",
    "scikit-learn==1.0",
    "pyarrow==6.0.0",
]

remote_packages = [
    "dask==2021.9.1",
    "dask-ml==1.9.0",
    "distributed==2021.9.1",
    "blosc==1.10.6",
    "lz4==3.1.3",
    "s3fs==2021.10.1",
]

test_packages = [
    "pytest==6.2.5",
]

development_packages = [
    "black==21.9b0",
    "isort==5.9.3",
    "setuptools",
    "wheel",
    "twine",
    "ipykernel",
]

nlp_packages = [
    "stop-words==2018.7.23",
    "yake==0.4.8",
    "gensim==4.1.2",
    "spacy==3.2.0",
    "nltk==3.6.5",
]

setup(
    name="quantile-data-kit",
    version="0.0.16",
    author="Jules Huisman",
    author_email="jules.huisman@quantile.nl",
    description="An internal Quantile development kit for making working with data easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quantile-development/quantile-data-kit",
    project_urls={
        "Bug Tracker": "https://github.com/quantile-development/quantile-data-kit/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        *default_packages,
        *remote_packages,
        *nlp_packages,
    ],
    extras_require={
        "remote": [
            *remote_packages,
        ],
        "nlp": [
            *nlp_packages,
        ],
        "test": [
            *test_packages,
        ],
        "development": [
            *development_packages,
            *test_packages,
        ],
    },
    packages=find_packages(),
    python_requires=">=3.8",
)
