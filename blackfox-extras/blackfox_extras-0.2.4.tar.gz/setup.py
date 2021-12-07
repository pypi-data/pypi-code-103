# coding: utf-8

"""
    BlackFoxExtras

    BlackFoxExtras

"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "blackfox_extras"
VERSION = "0.2.4"

REQUIRES = [
    "blackfox >= 5.1.1",
    "numpy >= 1.21.4, <=1.21.4",
    "scikit-learn >=1.0.1, <=1.0.1",
    "pandas >=1.3.4, <=1.3.4",
    "category_encoders >=2.3.0, <=2.3.0",
    "tensorflow >=2.7.0, <=2.7.0",
    "xgboost >=1.5.0, <=1.5.0"
    ]

setup(
    name=NAME,
    version=VERSION,
    description="BlackFox Extras",
    author="Tomislav Mrdja",
    author_email="",
    url="https://github.com/vodena/BlackFoxPythonExtras",
    keywords=["BlackFox"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test.*", "test"]),
    include_package_data=True,
    long_description="""\
        BlackFox Extras
    """
)
