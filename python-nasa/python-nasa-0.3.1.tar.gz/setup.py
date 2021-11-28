from typing import List, Text
import nasa

from setuptools import setup

with open("README.md") as readme_file:
    readme: Text = readme_file.read()

requirements: List[Text] = ["requests", "pillow"]

test_requirements: List[Text] = ["requests", "pre-commit", "pillow", "wheel"]

setup(
    name="python-nasa",
    version=nasa.__version__,
    description="Unofficial Python Wrapper for NASA API",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/wrap-api/python-nasa",
    download_url="https://github.com/wrap-api/python-nasa/archive/main.tar.gz",
    author=nasa.__author__,
    author_email=nasa.__email__,
    packages=["nasa"],
    package_dir={"nasa": "nasa"},
    include_package_data=True,
    license="MIT",
    install_requires=requirements,
    tests_require=test_requirements,
    keywords="nasa planet astronomy image galaxy earth",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
