# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyechelle']

package_data = \
{'': ['*']}

install_requires = \
['Autologging>=1.3.2,<2.0.0',
 'astropy>=5.0,<6.0',
 'h5py>=3.1.0,<4.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'numba>=0.54.1,<0.55.0',
 'numpy==1.20.3',
 'pandas>=1.3.4,<2.0.0',
 'parmap>=1.5.2,<2.0.0',
 'plotly>=5.4.0,<6.0.0',
 'scipy>=1.5.2,<2.0.0']

extras_require = \
{'optional_dep': ['skycalc-ipy>=0.1.3,<0.2.0', 'astroquery>=0.4.4,<0.5.0']}

entry_points = \
{'console_scripts': ['pyechelle = pyechelle.simulator:main']}

setup_kwargs = {
    'name': 'pyechelle',
    'version': '0.1.6',
    'description': 'A fast generic spectrum simulator',
    'long_description': '# PyEchelle\n\nPyEchelle is a simulation tool, to generate realistic 2D spectra, in particular cross-dispersed echelle spectra.\nHowever, it is not limited to echelle spectrographs, but allows simulating arbitrary spectra for any fiber-fed or slit\nspectrograph, where a model file is available. Optical aberrations are treated accurately, the simulated spectra include\nphoton and read-out noise.\n\n### Example usage\n\n```bash\npyechelle --spectrograph MaroonX --fiber 2-4 --sources Phoenix --phoenix_t_eff 3500 -t 10 --rv 100 -o mdwarf.fit\n```\n\nsimulates a PHOENIX M-dwarf spectrum with the given stellar parameters, and a RV shift of 100m/s for the MAROON-X\nspectrograph.\n \nThe output is a 2D raw frame (.fits) and will look similar to:\n\n![](https://gitlab.com/Stuermer/pyechelle/-/raw/master/docs/source/_static/plots/mdwarf.jpg "")\n\nCheck out the [Documentation](https://stuermer.gitlab.io/pyechelle/usage.html) for more examples.\n\nPyechelle is the successor of [Echelle++](https://github.com/Stuermer/EchelleSimulator) which has a similar\nfunctionality but was written in C++. This package was rewritten in python for better maintainability, easier package\ndistribution and for smoother cross-platform development.\n\n# Installation\n\nAs simple as\n\n```bash\npip install pyechelle[optional_dep]\n```\n\nHere, adding *[optional_dep]* will also install optional dependencies (e.g. astroquery, skycalc-ipy) for supporting all\nfeatures such as atmosphere tellurics.\n\nCheck out the [Documentation](https://stuermer.gitlab.io/pyechelle/installation.html) for alternative installation instruction.\n\n# Usage\n\nSee\n\n```bash\npyechelle -h\n```\n\nfor all available command line options.\n\nSee [Documentation](https://stuermer.gitlab.io/pyechelle/usage.html) for more examples.\n\n# Citation\n\nPlease cite this [paper](http://dx.doi.org/10.1088/1538-3873/aaec2e) if you find this work useful in your research.\n',
    'author': 'Julian Stuermer',
    'author_email': 'julian@stuermer.science',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/Stuermer/pyechelle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
