import pathlib
from setuptools import setup, find_packages
from subnetfinder.__init__ import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="subnetfinder",
    version=__version__,
    python_requires='>=3.7',
    description="Find available subnets within a given block of IPs",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://sourceforge.net/projects/available-subnet-finder/",
    author="Skylight 2000",
    #author_email="",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    #packages=["subnetfinder"],
    scripts=[],
    packages=find_packages(include=['subnetfinder','subnetfinder.*'],exclude=('tests',)),
    include_package_data=True,
    #install_requires=["math", "sys", "ipaddress"],
    entry_points={
        'console_scripts': [
            'subnetfinder=subnetfinder.__main__:main'
        ],
        'subnetfinder': [
            'ProcessSubnets=subnetfinder.subnetfinder:ProcessSubnets'
        ]
    }
)
