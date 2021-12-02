from setuptools import setup

__project__ = "verifypacks"
__version__ = "0.0.1"
__description__ = "this library verifies if python libraries are up to date"
__packages__ = ["verifypacks"]
__author__ = "Kaio Marques"
__requires__ = ["piprot"]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    requires = __requires__,
)