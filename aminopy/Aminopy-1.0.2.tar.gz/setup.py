from setuptools import setup, find_packages
from amino.__init__ import __license__, __title__, __version__, __author__

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name=__title__,
    version=__version__,
    url="https://github.com/Oustex/Aminopy",
    download_url="https://github.com/Oustex/Aminopy/tarball/master",
    license=__license__,
    author=__author__,
    author_email="oustexp@gmail.com",
    description="A library to create Amino bots.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "aminoapps",
        "amino-py",
        "amino",
        "amino-bot",
        "narvii",
        "api",
        "oustex",
        "slimakoi",
        "aminopy",
        "official"
    ],
    install_requires=[
        "setuptools",
        "requests",
        "six",
        "websocket-client==0.57.0",
        "json_minify",
        "Amino-Socket"
    ],
    setup_requires=["wheel"],
    packages=find_packages()
)
