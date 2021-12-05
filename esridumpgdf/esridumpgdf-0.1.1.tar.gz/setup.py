# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esridumpgdf']

package_data = \
{'': ['*']}

install_requires = \
['esridump>=1.10.1,<2.0.0', 'geopandas>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'esridumpgdf',
    'version': '0.1.1',
    'description': '',
    'long_description': "# esridumpgdf\n\nSimple module using [pyesridump](https://github.com/openaddresses/pyesridump) \nand [geopandas](https://github.com/geopandas/geopandas) to create GeoDataFrames from \nArcGIS Map and Feature layers and services.  \n\n## Install\n```\npip install esridumpgdf\n```\n\n## Usage\nFor exporting a single Map or Feature service to GeoDataFrame:\n```python\nfrom esridumpgdf import Layer\nlayer = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/911CallsHotspot/MapServer/1'\ngdf = Layer(layer).to_gdf()\n```\n\nTo export an entire service to a multiple GeoDataFrames:\n```python\nfrom esridumpgdf import Service\nservice = 'https://sampleserver6.arcgisonline.com/arcgis/rest/services/Wildfire/MapServer'\ngdfs = Service(service).to_gdfs()\n```",
    'author': 'wchatx',
    'author_email': 'wchatx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
