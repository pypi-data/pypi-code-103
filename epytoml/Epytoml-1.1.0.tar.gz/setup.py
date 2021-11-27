import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = "1.1.0"
PACKAGE_NAME = "Epytoml"
AUTHOR = "Zhean Robby Ganituen"
AUTHOR_EMAIL = "zheanrobbyganituen@gmail.com"
URL = "https://github.com/Z1aaan/Epytoml"

LICENSE = "MIT License"
DESCRIPTION = "A python package that converts plain text into a specified markup language using python."
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    "pdfkit",
    "lorem",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
)
