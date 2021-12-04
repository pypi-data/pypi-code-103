import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
# README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sda_printer",
    version="1.0.6",
    description="Description",
    # long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="Eimantas SDA",
    author_email="eima.blaz@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["sda_printer"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "sda_printer=sda_printer.__main__:very_cool_hi",
        ]
    },
)