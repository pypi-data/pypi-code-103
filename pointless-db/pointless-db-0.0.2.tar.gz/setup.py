import os
import re

from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


def get_variable(variable):
    with open(os.path.join("pointless_db", "__init__.py")) as f:
        return re.search(
            "{} = ['\"]([^'\"]+)['\"]".format(variable), f.read()
        ).group(1)  # type: ignore


setup(
    name="pointless-db",
    version=get_variable("__version__"),
    url=get_variable("__url__"),
    description=get_variable("__description__"),
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author=get_variable("__author__"),
    author_email="wardpearce@pm.me",
    license="GPL-3.0",
    py_modules=["plugin"],
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False
)
