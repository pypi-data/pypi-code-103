# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['backend_library_common', 'backend_library_common.utils']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0', 'httpx>=0.21.1,<0.22.0', 'pydantic>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'backend-library-common',
    'version': '0.1.5',
    'description': '',
    'long_description': 'backend_library_common\nhttps://pypi.org/project/backend-library-common/\n```\npoetry build\npoetry publish\n```\n',
    'author': 'Felix',
    'author_email': 'contact@felixnaser.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/intelligence-for-robots/backend.library.common',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
