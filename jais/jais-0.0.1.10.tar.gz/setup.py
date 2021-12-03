#!/usr/bin/env python
from setuptools import setup, find_packages
from jais.__init__ import NAME, VERSION, DESCRIPTION
from jais.utils.fileloader import save_json

NAME = NAME.lower()

with open("requirements.txt") as rf:
    REQUIREMENTS = [l.strip() for l in rf.read().split("\n")]

with open('README.md') as rf:
    LONG_DESCRIPTION = rf.read()

save_json({},f'{NAME}/configs/{NAME}_settings.json')

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      author='Jitender Singh Virk',
      author_email='krivsj@gmail.com',
      url='https://virksaab.github.io',
      packages=find_packages(exclude=['ez_setup', 'tests*', ".github"]),
      # package_data={'jais': ['data/*.dat']},
      include_package_data=True,
      install_requires=REQUIREMENTS,
      setup_requires=['wheel'],
      entry_points=f"""
        [console_scripts]
        {NAME}={NAME}.main:cli
      """)
