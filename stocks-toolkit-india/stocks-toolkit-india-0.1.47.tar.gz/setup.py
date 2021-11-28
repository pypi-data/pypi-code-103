from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

README = (HERE/"README.md").read_text()

classifiers = [
    "License :: OSI Approved :: MIT License", 
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3", 
    "Programming Language :: Python :: 3.7"
]


setup(
    name = "stocks-toolkit-india",
    version="0.1.47",
    description="Toolkit for performing analysis on indian stock market",
    long_description=README,
    long_description_content_type="text/markdown", 
    url="https://github.com/Colo55us/stocks_toolkit_india",
    author = "Mohit Pratap Singh",
    author_email="mohit.planed@gmail.com",
    license="MIT",
    classifiers=classifiers,
    packages= find_packages(),
    include_package_data=True,
    install_requires = ["numpy","pandas","TA-lib","requests","datetime","bs4"],
)