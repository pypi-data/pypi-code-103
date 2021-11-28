#!/usr/bin/env python
from setuptools import setup
from pathlib import Path

basedir = Path(__file__).resolve().parent
readme = (basedir / "README.md").read_text()

setup(
    name='tcim',
    version='0.1.0',
    description='terminal commands in menus',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/wups/tcim',
    author='wups',
    license='GNU GPLv3',
    packages=['tcim'],
    scripts=[
        'bin/tcim-dmenu',
        'bin/tcim-update-xdg-menu'
    ],
    package_data={'tcim': ['command-menu.directory', 'commands.tsv']},
)
