import sys
import os
import setuptools

sys.path[0:0] = ['curvenote']
from version import __version__


def readme():
    if os.path.exists("README.rst"):
        with open("README.rst") as file:
            return file.read()
    return ""


setuptools.setup(
    name="curvenote",
    description="Helper library for curvenote versioning and tracking with Jupyter notebooks",
    long_description=readme(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Text Processing :: Linguistic",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Financial and Insurance Industry",
    ],
    entry_points='''
        [console_scripts]
        curvenote=curvenote.__main__:main
    ''',
    url="http://curvenote.com",
    version=__version__,
    author="iooxa inc.",
    author_email="hi@curvenote.com",
    packages=setuptools.find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "pydantic",
        "requests",
        "typer",
        "pyyaml",
        "jtex==0.3.4"
    ],
    python_requires=">=3.7",
)
