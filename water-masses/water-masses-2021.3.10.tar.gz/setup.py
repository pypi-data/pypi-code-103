# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['water_masses',
 'water_masses.data',
 'water_masses.origin',
 'water_masses.tracmass']

package_data = \
{'': ['*']}

install_requires = \
['cf-xarray>=0.5,<1.0',
 'cftime>=1.2,<2.0',
 'dask>=2021.1,<2022.0',
 'eofs>=1.4.0,<2.0.0',
 'h5netcdf>=0.10,<1.0',
 'intake-xarray>=0.4,<1.0',
 'intake>=0.6,<1.0',
 'nc-time-axis>=1.2,<2.0',
 'netcdf4>=1.5,<2.0',
 'numpy>=1.19,<2.0',
 'pandas>=1.1,<2.0',
 'scipy>=1.7,<2.0',
 'statsmodels>=0.12,<1.0',
 'xarray>=0.16,<1.0']

setup_kwargs = {
    'name': 'water-masses',
    'version': '2021.3.10',
    'description': 'Analysis of the northern European shelf seas',
    'long_description': '# Water-Masses\n[![Build Status](https://github.com/shelf-sea/water-masses/workflows/test/badge.svg?branch=master&event=push)](https://github.com/shelf-sea/water-masses/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/shelf-sea/water-masses/branch/master/graph/badge.svg)](https://codecov.io/gh/shelf-sea/water-masses)\n[![Python Version](https://img.shields.io/pypi/pyversions/water-masses.svg)](https://pypi.org/project/water-masses/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nAnalysis of the northern Eurpean shelf seas.\n\n## Installation\n\n```bash\npip install water-masses\n# or\npoetry add git+https://github.com/shelf-sea/water-masses.git#trunk\n```\n\n## License\n\n[gpl3](https://github.com/shelf-sea/water-masses/blob/master/LICENSE)\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [98c82c2c9f7f66fd8a5009361e4272240c25dc6f](https://github.com/wemake-services/wemake-python-package/tree/98c82c2c9f7f66fd8a5009361e4272240c25dc6f). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/98c82c2c9f7f66fd8a5009361e4272240c25dc6f...master) since then.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/shelf-sea/water-masses',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
