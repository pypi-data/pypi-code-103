from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    author="Peter Raso",
    description="A simple package for db connection.",
    name="brtgdb",
    version="0.3.5",
    packages=find_packages(include=["brtgdb"]),
    install_requires=['SQLAlchemy>1.4.20'],  # 
    python_requires='>=3.7',
    long_description=long_description,
    long_description_content_type='text/markdown'
)