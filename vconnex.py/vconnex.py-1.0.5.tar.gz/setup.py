from setuptools import find_packages, setup
from vconnex import __version__

def get_requirements():
    with open("requirements.txt") as file:
        return [line.strip() for line in file]

def get_long_desc():
    with open("README.md", encoding="utf-8") as file:
        return file.read()


setup(
    name='vconnex.py',
    version=__version__,
    author='Vconnex Inc.',
    keywords="vconnex python",

    description='A Python library for Vconnex Open API',
    long_description=get_long_desc(),
    long_description_content_type="text/markdown",

    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=get_requirements(),
    license='MIT',
)