# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['micropub']

package_data = \
{'': ['*']}

install_requires = \
['nltk>=3.6.5,<4.0.0', 'understory>=0,<1']

entry_points = \
{'console_scripts': ['micropub = micropub.__main__:main']}

setup_kwargs = {
    'name': 'micropub',
    'version': '0.0.4',
    'description': 'A library for writing Micropub servers and clients.',
    'long_description': "# micropub-python\n\nA library for writing [Micropub][0] servers and clients.\n\n> The Micropub protocol is used to create, update and delete posts on\n> one's own domain using third-party clients. Web apps and native apps\n> (e.g., iPhone, Android) can use Micropub to post and edit articles,\n> short notes, comments, likes, photos, events or other kinds of posts\n> on your own website.\n\n[0]: https://micropub.spec.indieweb.org/\n",
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
