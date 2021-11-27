"""Setup script for PYRALYSIS"""
import os.path

from setuptools import find_packages
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="pyralysis",
    version="0.1.10",
    description="PYthon Radio Astronomy anaLYSis and Image Synthesis",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/miguelcarcamov/pyralysis",
    author="Miguel Cárcamo",
    author_email='miguel.carcamo@manchester.ac.uk',
    license='GNU',
    install_requires=["numpy", "astropy", "joblib", "cupy", "python-casacore", "numba", "dask", "dask-ms[xarray]", "more-itertools"],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"],
)
