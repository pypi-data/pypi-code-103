
from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

#get version
with open(path.join(this_directory, 'VERSION'), encoding='utf-8') as f:
    version = f.read()

setup(
    name='radvelso',
    version=version,
    url='https://gitlab.science.gc.ca/dlo001/radvelso',
    license='GPL-3.0-or-later',
    author='David Lobon',
    author_email='dhlobon@gmail.com',
    description="radvelso's tools for superobs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),    
    python_requires='>=3.8', 
    install_requires=['numpy >= 1.17.0','cartopy==0.19.0','domutils' ,'dask', 'scipy', 'pytz'],
)
