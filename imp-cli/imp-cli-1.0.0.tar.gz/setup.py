from setuptools import setup, find_packages
from io import open
from os import path
from os import walk
import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt
with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (
    not x.startswith('#')) and (not x.startswith('-'))]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs \
                    if 'git+' not in x]
def package_files(directory):
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append(path.join('..', path, filename))
    return paths

# extra_files = package_files('/files_template')

#  package_data={'': extra_files},

setup (
 name = 'imp-cli',
 description = 'A simple commandline app for create project',
 version = '1.0.0',
 packages = find_packages(), # list of all packages
 package_data={
     'imp-cli.files_template': ['*','*/*','*/*/*'],
 },
 install_requires = install_requires,
 python_requires='>=3.7', # any python greater than 2.7
 entry_points={
     'console_scripts' : [
         'imp-cli=imperiums_cli.main:main'
     ],
 },
 author="Johan Manuel Bustos Mendoza",
 keyword="imperiums, dashboard, bi",
 long_description=README,
 long_description_content_type="text/markdown",
 license='MIT',
#  url='https://github.com/CITGuru/cver',
#  download_url='https://github.com/CITGuru/cver/archive/1.0.0.tar.gz',
  dependency_links=dependency_links,
  author_email='johan.bustosm@gmail.com',
)