from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="python-pancakeswap",
    version="0.0.5",
    author="tinghsuwan",
    author_email="wanth1997@gmail.com",
    description="Python pancakeswap",
    license="MIT",
    url="https://github.com/LeagueOfBlockchain/python-pancakeswap",
    packages=["pancakeswap"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["web3", "loguru"],
    zip_safe=True,
)
