# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nenucal', 'nenucal.tests', 'nenucal.tools']

package_data = \
{'': ['*'], 'nenucal': ['cal_config/*', 'templates/*']}

install_requires = \
['GPy>=1.9.9,<2.0.0',
 'astropy>=3.2,<5.0',
 'astroquery>=0.4',
 'click>=7.0,<8.0',
 'libpipe>=0.1.1',
 'losoto>=2.0,<3.0',
 'matplotlib>=3.0,<4.0',
 'nenupy>=1.0,<2.0',
 'python-casacore>=3.0,<4.0',
 'requests>=2.0,<3.0',
 'scipy>=1.4,<2.0',
 'tables>=3.2,<4.0',
 'tabulate>=0.8',
 'toml>=0.10']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['calpipe = nenucal.tools.calpipe:main',
                     'flagtool = nenucal.tools.flagtool:main',
                     'imgpipe = nenucal.tools.imgpipe:main',
                     'modeltool = nenucal.tools.modeltool:main',
                     'nenudata = nenucal.tools.nenudata:main',
                     'soltool = nenucal.tools.soltool:main']}

setup_kwargs = {
    'name': 'nenucal',
    'version': '0.1.98',
    'description': 'Calibration pipeline for the NenuFAR Cosmic Dawn project',
    'long_description': 'NenuCAL CD\n==========\n\nCalibration pipeline and set of utilities for the NenuFAR Cosmic Dawn project. The calibration uses the standard LOFAR [DPPP](https://github.com/lofar-astron/DP3/tree/master/DPPP) in the background and should be general enough to be used by any NenuFAR projects.\n\nInstallation\n------------\n\nnenucal-cd can be installed via pip:\n\n    $ pip install nenucal-cd\n\nand requires Python 3.7.0 or higher. For most tasks, you will also need [DPPP](https://github.com/lofar-astron/DP3/tree/master/DPPP), [LSMTool](https://www.astron.nl/citt/lsmtool/overview.html) that you can install with the command:\n\n    $ pip install git+https://github.com/darafferty/LSMTool.git\n\nand [LoSoTo](https://revoltek.github.io/losoto/) that you can install with the command:\n\n    $ pip install git+https://github.com/revoltek/losoto\n\nUsage\n-----\n\nCalibration is performed using the `calpipe` utility. You will find [here some documentations](https://gitlab.com/flomertens/nenucal-cd/-/wikis/Calibrating-NenuFAR-data) on how to use it.\n\nAdditionally to calpipe, this package provides a tool to manage the FLAG column and run a SSINS flagger ([flagtool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/flagging-utility)), a tool to plot and smooth gain solutions ([soltool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/soltool-utility)) and a tool to produce apparent sky model from catalog ([modeltool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/sky-model-utility)).\n\nContact\n-------\n\nDo not hesitate to fill an [issue](https://gitlab.com/flomertens/nenucal-cd/-/issues) or contact me if you encounter a problem with this package.\n',
    'author': '"Florent Mertens"',
    'author_email': '"florent.mertens@gmail.com"',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/flomertens/nenucal-cd',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
