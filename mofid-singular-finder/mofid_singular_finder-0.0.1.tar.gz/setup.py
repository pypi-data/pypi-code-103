from setuptools import find_packages, setup
# read the contents of your README file
from os import path
from mofid_singular_finder.version import __version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

exec(open('mofid_singular_finder/version.py').read())
setup(
    name='mofid_singular_finder',
    packages=find_packages(include=['mofid_singular_finder']),
    version=__version__,
    description='A simple library for finding words with Second person singular pronouns.',
    author='ali96ebrahimi@gmail.com',
    license='MIT',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
