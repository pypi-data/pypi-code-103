# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zodipy']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'astropy>=4.3.1,<5.0.0',
 'astroquery>=0.4.3,<0.5.0',
 'h5py>=3.6.0,<4.0.0',
 'healpy>=1.15.0,<2.0.0',
 'numba>=0.54.1,<0.55.0',
 'numpy>=1.15',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'zodipy',
    'version': '0.3.2',
    'description': 'Zodipy is a python tool that simulates the Zodiacal emission.',
    'long_description': '\n<img src="imgs/zodipy_logo.png" width="350">\n\n[![PyPI version](https://badge.fury.io/py/zodipy.svg)](https://badge.fury.io/py/zodipy)\n![Tests](https://github.com/MetinSa/zodipy/actions/workflows/tests.yml/badge.svg)\n[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)\n\n\n---\n\n\n*Zodipy* is a Python simulation tool for Zodiacal Emission (Interplanetary Dust Emission). It allows you to compute the \nsimulated emission in a timestream, or at an instant in time.\n\n![plot](imgs/zodi_default.png)\n\n## Installing\nZodipy is available at PyPI and can be installed with ``pip install zodipy``.\n\n## Features\nThe full set of features and use-cases will be documentated in the nearby future.\n\n**Initializing an Interplantery Dust Model:** We start by selecting which Interplanetary Dust Model to use. Currently, the implemented options are the [Kelsall et al. (1998)](https://ui.adsabs.harvard.edu/abs/1998ApJ...508...44K/abstract) model with or without the various emissivity fits from the Planck collaboration.\n```python\nimport zodipy\n\n# Other options for models are "K98", "Planck13", "Planck15"\nmodel = zodipy.InterplanetaryDustModel(model="Planck18")\n```\n\n**Instantaneous emission:** By obtaining the coordinates of an observer through the JPL Horizons API, we can simulate the full sky at an instant in time as follows:\n```python\nimport healpy as hp\n\nepoch = 59215  # 2010-01-01 in Modified Julian dates\nemission = model.get_instantaneous_emission(\n    nside=256, \n    freq=800, \n    observer="Planck", \n    epochs=epoch\n)\n\nhp.mollview(emission, norm="hist", coord=["E", "G"])\n```\n![plot](imgs/zodi_planck.png)\n\nThe `epochs` input must follow the convention used in [astroquery](https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html). If multiple dates are used as epochs, the returned emission will be the average emission over all instantaneous maps.\n\nAdditionally, it is possible to retrieve the emission of each Zodiacal Component in a dictionary, if the parameter `return_comps` is set to `True`. Following is an example of what each component may have looked like at 6th of October 2021.\n\n![plot](imgs/comps.png)\n\n\n**Time-ordered emission:** For a chunk of time-ordered data, it is possible to compute the simulated Zodiacal Emission over each observed pixel. In the following example we simulate the Zodiacal Emission time-stream given a chunk of the time-ordered pixels from the DIRBE instrument of the COBE satellite (Photometric Band 8, Detector A, first day of observations):\n```python\nimport matplotlib.pyplot as plt\nimport zodipy\n\nmodel = zodipy.InterplanetaryDustModel(model="K98")\n\ndirbe_pixel_timestream = ...    # Get in DIRBE tods\ndirbe_coords = ...  # Get coords of DIRBE at the time corresponding to the tod chunk \nearth_coords = ... # Get coords of the Earth at the time corresponding to the tod chunk \ndirbe_freq = 974    # GHz\ndirbe_nside = 128\n\ntimestream = model.get_time_ordered_emission(\n    nside=dirbe_nside,\n    freq=dirbe_freq,\n    pixels=dirbe_pixel_timestream,\n    observer_coordinates=dirbe_coords,\n    earth_coordinates=earth_coords\n)\n\nplt.plot(timestream)\n```\n![plot](imgs/timestream.png)\n\n\n**Binned time-ordered emission:** By setting the optional `bin` parameter to `True`, the emission is binned into a map which we can visualize as follows:\n\n```python\n\n# Get three tod chunks, each corresponding to a day of observation\npixel_chunks = [...]\ndirbe_coords = [...]\nearth_coords = [...]\n\n# Initialize empty emission and hit maps array\nemission = np.zeros(hp.nside2npix(nside))\nhits_map = np.zeros(hp.nside2npix(nside))   \n    \n    # Loop over tod chunks\n    for pixels, dirbe_coords, earth_coords in zip(pixel_chunks, dirbe_coords, earth_coords)):\n        \n        # We construct the total hits map over all chunks so that we can\n        # normalize the output map\n        unique_pixels, counts = np.unique(pixels, return_counts=True)\n        hits_map[unique_pixels] += counts\n\n        emission += model.get_time_ordered_emission(\n            freq=freq,\n            nside=nside,\n            pixels=pixels,\n            observer_coordinates=dirbe_coords,\n            earth_coordinates=earth_coords,\n            bin=True,\n        )\n\nemission /= hits_map\n\nhp.mollview(emission, norm="hist", coord=["E", "G"])\n```\n![plot](imgs/binned.png)\n',
    'author': 'Metin San',
    'author_email': 'metinisan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MetinSa/zodipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
