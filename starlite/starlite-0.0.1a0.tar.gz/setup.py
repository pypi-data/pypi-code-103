# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['starlite', 'starlite.utils']

package_data = \
{'': ['*']}

install_requires = \
['pydantic', 'starlette', 'typing-extensions']

setup_kwargs = {
    'name': 'starlite',
    'version': '0.0.1a0',
    'description': 'Light-weight and flexible ASGI API Framework',
    'long_description': '# starlite\n\nPre-Alpha WIP.\n',
    'author': "Na'aman Hirschfeld",
    'author_email': 'Naaman.Hirschfeld@sprylab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Goldziher/starlite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
