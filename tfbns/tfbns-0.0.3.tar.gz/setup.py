import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfbns",
    version="0.0.3",
    author="Srinivas T R",
    author_email="srinivasraman18@gmail.com",
    description="A Python package for Term Frequency - Binomial Seperation feature scaling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/srinivasraman18/tfbns",
    packages=setuptools.find_packages(),
    install_requires = ['pandas','swifter','scipy','scikit-learn'] ,
    dependency_links=[
        'https://pypi.org/project/pandas/',
        'https://pypi.org/project/swifter/',
        'https://pypi.org/project/scipy/',
        'https://pypi.org/project/scikit-learn/'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)