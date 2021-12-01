# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['microformats']
install_requires = \
['mf2py>=1.1.2,<2.0.0', 'mf2util>=0.5.1,<0.6.0', 'understory>=0,<1']

setup_kwargs = {
    'name': 'microformats',
    'version': '0.0.6',
    'description': 'A Microformats parser and utilities.',
    'long_description': '# microformats-python\n\nA [Microformats][0] parser and utilities.\n\n> Designed for humans first and machines second, microformats are a set\n> of simple, open data formats built upon existing and widely adopted\n> standards. Instead of throwing away what works today, microformats\n> intend to solve simpler problems first by adapting to current behaviors\n> and usage patterns.\n\n[0]: https://microformats.org\n',
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
