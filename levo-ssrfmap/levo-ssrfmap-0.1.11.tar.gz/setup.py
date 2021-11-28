# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ssrfmap', 'ssrfmap.core', 'ssrfmap.handlers', 'ssrfmap.modules']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'levo-commons>=0.1.9,<0.2.0',
 'requests>=2.25.1,<3.0.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['ssrfmap = ssrfmap.cli:ssrfmap']}

setup_kwargs = {
    'name': 'levo-ssrfmap',
    'version': '0.1.11',
    'description': "A packaged version of SSRFmap, for use with Levo.ai's CLI.",
    'long_description': None,
    'author': 'Swissky',
    'author_email': None,
    'maintainer': 'Akshath Kothari',
    'maintainer_email': 'akshath.kothari@levo.ai',
    'url': 'https://levo.ai',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
