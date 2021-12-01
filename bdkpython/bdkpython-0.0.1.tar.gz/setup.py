import pathlib
from setuptools import setup, find_packages


README = (pathlib.Path(__file__).parent / "./README.md").read_text()

setup(
    name='bdkpython',
    version='0.0.1',
    description="Python language bindings for the bitcoindevkit",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bitcoindevkit/bdk-ffi",
    author="Alekos Filini <alekos.filini@gmail.com>, Steve Myers <steve@notmandatory.org>",
    license="MIT or Apache 2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
