# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['census_shapefiles']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'census-shapefiles',
    'version': '1.1.2',
    'description': 'Library to get census shapefiles',
    'long_description': '## Census Shapefiles\n\nLibrary to pull shapefiles from the Census\n\n### Installation\n```\npip install census-shapefiles\n```\n\n### Usage\n```python\nfrom census_shapefiles import CensusShapefiles\n\nsfs = CensusShapeFiles()\nfor shapefile in sfs.city.get_shapefiles():\n    # Do something with the temp file\n```',
    'author': 'Zach Perkitny',
    'author_email': 'zperkitny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/zachperkitny/census-shapefiles',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
