#!/usr/bin/env python

from setuptools import setup

setup(name='MagicPy',
      version='0.1',
      description='Toolbox to control MagVenture TMS stimulators',
      author='Ole Numssen',
      author_email='numssen@posteo.de',
      url='https://gitlab.gwdg.de/tms-localization/utils/magicpy',
      packages=['magicpy'],
      install_requires=['pyserial>=3.5', 'numpy>=1.20.0']
      )
