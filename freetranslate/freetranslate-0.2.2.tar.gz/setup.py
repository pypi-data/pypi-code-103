import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="freetranslate",
    version="0.2.2",
    description="Another translate API for Python.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/tretrauit/freetranslate",
    author="tretrauit",
    author_email="tretrauit@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    packages=["freetranslate"],
    include_package_data=True,
    install_requires=["aiohttp"]
)