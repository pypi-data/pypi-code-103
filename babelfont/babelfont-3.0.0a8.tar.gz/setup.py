# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['babelfont', 'babelfont.convertors', 'babelfont.fontFilters']

package_data = \
{'': ['*']}

install_requires = \
['cu2qu>=1.6.7,<2.0.0',
 'fontfeatures>=1.0.6,<2.0.0',
 'fonttools>=4.21.1',
 'glyphsLib>=5.3.2',
 'openstep-plist>=0.2.2',
 'orjson>=3.5.1,<4.0.0',
 'ufoLib2>=0.11.1']

entry_points = \
{'console_scripts': ['babelfont = babelfont.__main__:main']}

setup_kwargs = {
    'name': 'babelfont',
    'version': '3.0.0a8',
    'description': '',
    'long_description': None,
    'author': 'Simon Cozens',
    'author_email': 'simon@simon-cozens.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
}


setup(**setup_kwargs)
