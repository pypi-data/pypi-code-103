# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aisexplorer']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.6.4,<5.0.0', 'pandas>=1.3.4,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'aisexplorer',
    'version': '0.0.3',
    'description': 'Wrapper to fetch data from marinetraffic',
    'long_description': '# AISExplorer\nAISExplorer can be used to locate vessels or to scrape all vessely in an AREA. \nAlso free proxies can be used out of the box.\n\n## Installation\n\n```\npip install aisexplorer\n```\n\n## Usage\n\n### Find vessel by MMIS\n\n```\nimport aisexplorer\n\nfrom ais_explorer.AIS import get_location\n\nget_location(211281610)\n```\n\n### Find vessels in Area\n\n**maximum 500 vessels**\n\n```\nimport aisexplorer\n\nfrom ais_explorer.AIS import get_area_data\n\nget_area_data("EMED", return_df= True)\n```\nOutput is limited to 500 rows.\n[Areas](https://help.marinetraffic.com/hc/en-us/articles/214556408-Areas-of-the-World-How-does-MarineTraffic-segment-them-) can be found here\n\n## Next Steps\n\n- Add filters to Area Function\n- Add Fallbacks if proxies has died\n- Add docstrings to functions\n\n## Changelog\n\n### 2021-11-27\n\n- Added Proxy Option\n\n\n\n\n\n\n',
    'author': 'reyemb',
    'author_email': 'reyemb.coding@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/reyemb/AISExplorer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
