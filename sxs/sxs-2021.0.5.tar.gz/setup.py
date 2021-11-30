# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sxs',
 'sxs.catalog',
 'sxs.horizons',
 'sxs.metadata',
 'sxs.utilities',
 'sxs.utilities.decimation',
 'sxs.utilities.lvcnr',
 'sxs.utilities.references',
 'sxs.waveforms',
 'sxs.zenodo',
 'sxs.zenodo.api']

package_data = \
{'': ['*']}

install_requires = \
['feedparser>=6.0.1,<7.0.0',
 'h5py>=3,<4',
 'inflection>=0.5.1,<0.6.0',
 'numpy>=1.15,<2.0',
 'pandas>=1.1.2,<2.0.0',
 'pylatexenc>=2.7,<3.0',
 'pytest-forked>=1.3.0,<2.0.0',
 'pytz>=2020.1,<2021.0',
 'quaternionic>=1.0,<2.0',
 'requests>=2.24.0,<3.0.0',
 'scipy>=1.0,<2.0',
 'spherical>=1.0,<2.0',
 'tqdm>=4.48.2,<4.61.2',
 'urllib3>=1.25.10,<2.0.0']

extras_require = \
{':implementation_name == "cpython"': ['numba>=0.50'],
 ':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'ecosystem': ['ipywidgets>=7.5.1,<8.0.0',
               'ipykernel>=5.3.4,<6.0.0',
               'jupyter_contrib_nbextensions>=0.5.1,<0.6.0',
               'jupyterlab>=2.2.8,<3.0.0',
               'line_profiler>=3.0.2,<4.0.0',
               'memory_profiler>=0.57.0,<0.58.0',
               'matplotlib>=2.1.1',
               'sympy>=1.6.2,<2.0.0',
               'corner>=2.1.0,<3.0.0',
               'qgrid>=1.3.1,<2.0.0',
               'rise>=5.6.1,<6.0.0',
               'quaternion>=0.3.1,<0.4.0'],
 'ecosystem:sys_platform != "win32"': ['scri>=2020.8.18,<2021.0.0'],
 'mkapi:python_version >= "3.7"': ['mkapi==1.0.13'],
 'mkdocs:implementation_name == "cpython"': ['mkdocs>=1.1.2'],
 'pymdown-extensions:implementation_name == "cpython"': ['pymdown-extensions>=8,<9']}

setup_kwargs = {
    'name': 'sxs',
    'version': '2021.0.5',
    'description': 'Interface to data produced by the Simulating eXtreme Spacetimes collaboration',
    'long_description': '[![Test Status](https://github.com/sxs-collaboration/sxs/workflows/tests/badge.svg)](https://github.com/sxs-collaboration/sxs/actions)\n[![Documentation Status](https://readthedocs.org/projects/sxs/badge/?version=main)](https://sxs.readthedocs.io/en/main/?badge=main)\n[![PyPI Version](https://img.shields.io/pypi/v/sxs?color=)](https://pypi.org/project/sxs/)\n[![Conda Version](https://img.shields.io/conda/vn/conda-forge/sxs.svg?color=)](https://anaconda.org/conda-forge/sxs)\n[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/sxs-collaboration/sxs/blob/main/LICENSE)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/moble/sxs_notebooks/master)\n\n\n# Simulating eXtreme Spacetimes python package\n\nThe `sxs` python package provides a high-level interface for using data\nproduced by the SXS collaboration.  In particular, the function `sxs.load` can\nautomatically find, download, and load data, returning objects that provide\ncommon interfaces to the various types of data, without forcing the user to\nworry about details like data formats or where to find the data.  It can also\nautomatically select the newest or highest-resolution dataset for a given\nsimulation, or return a range of versions or resolutions.  Currently, the\nhigh-level objects encapsulate\n\n  * Catalog — a listing of all data produced by the SXS collaboration\n  * Metadata — data describing the simulation parameters\n  * Horizons — time-series data describing the apparent horizons\n  * Waveforms — time-series data describing the extrapolated gravitational-wave\n    modes\n\n\n## Installation\n\nBecause this package is pure python code, installation is very simple.  In\nparticular, with a reasonably modern installation, you can just run a command\nlike\n\n```bash\nconda install -c conda-forge sxs\n```\n\nor\n\n```bash\npython -m pip install sxs\n```\n\nHere, `conda` requires the [conda](https://docs.anaconda.com/anaconda/install/)\ninstallation of python, which is the most recommended approach for scientific\npython; the second command assumes that you have an appropriate python\nenvironment set up in some other way.  Either of these commands will download\nand install the `sxs` package and its most vital requirements.\n\nIf you want to install all the goodies that enable things like jupyter\nnotebooks with plots and interactive tables, you could run\n\n```bash\nconda install -c conda-forge sxs-ecosystem\n```\n\nor\n\n```bash\npython -m pip install sxs[ecosystem]\n```\n\nYou will probably also want to set some sensible defaults to automatically\ndownload and cache data:\n\n```bash\npython -c "import sxs; sxs.write_config(download=True, cache=True)"\n```\n\nThis will write a configuration file in the directory returned by\n`sxs.sxs_directory("config")`, and downloaded data will be cached in the\ndirectory returned by `sxs.sxs_directory("cache")`.  See [that function\'s\ndocumentation](api/sxs.utilities.sxs_directories/#sxsutilitiessxs_directoriessxs_directory)\nfor details.\n\n\n## Usage\n\nAn extensive demonstration of this package\'s capabilities is available\n[here](https://mybinder.org/v2/gh/moble/sxs_notebooks/master), in the form of\ninteractive jupyter notebooks that are actually running this code and some\npre-downloaded data.  The following is just a very brief overview of the `sxs`\npackage\'s main components.\n\nThere are four important objects to understand in this package:\n\n```python\nimport sxs\n\ncatalog = sxs.load("catalog")\nmetadata = sxs.load("SXS:BBH:0123/Lev/metadata.json")\nhorizons = sxs.load("SXS:BBH:0123/Lev/Horizons.h5")\nwaveform = sxs.load("SXS:BBH:0123/Lev/rhOverM", extrapolation_order=2)\n```\n\n[The `catalog` object](api/sxs.catalog.catalog/#sxs.catalog.catalog.Catalog)\ncontains information about every simulation in the catalog, including all\navailable data files, and information about how to get them.  You probably\ndon\'t need to actually know about details like where to get the data, but\n`catalog` can help you find the simulations you care about.  Most importantly,\n`catalog.simulations` is a `dict` object, where the keys are names of\nsimulations (like "SXS:BBH:0123") and the values are the same types as [the\n`metadata` object](api/sxs.metadata.metadata/#sxs.metadata.metadata.Metadata),\nwhich contains metadata about that simulation — things like mass ratio, spins,\netc.  This `metadata` reflects the actual output of the simulations, which\nleads to some inconsistencies in their formats.  A more consistent interface\n(though it is biased toward returning NaNs where a human might glean more\ninformation) is provided by `catalog.table`, which returns a\n[`pandas`](https://pandas.pydata.org/docs/) `DataFrame` with specific data\ntypes for each column.\n\nThe actual data itself is primarily contained in the next two objects.  [The\n`horizons` object](api/sxs.horizons/#sxs.horizons.Horizons) has three\nattributes — `horizons.A`, `horizons.B`, and `horizons.C` — typically\nrepresenting the original two horizons of the black-hole binary and the common\nhorizon that forms at merger.  In matter simulations, one or more of these may\nbe `None`.  Otherwise, each of these three is a\n[`HorizonQuantities`](api/sxs.horizons/#sxs.horizons.HorizonQuantities) object,\ncontaining several timeseries relating to mass, spin, and position.\n\nFinally, the\n[`waveform`](api/sxs.waveforms.waveform_modes/#sxs.waveforms.waveform_modes.WaveformModes)\nencapsulates the modes of the waveform and the corresponding time information,\nalong with relevant metadata like data type, spin weight, etc., and useful\nfeatures like numpy-array-style slicing.\n',
    'author': 'Michael Boyle',
    'author_email': 'michael.oliver.boyle@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sxs-collaboration/sxs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
