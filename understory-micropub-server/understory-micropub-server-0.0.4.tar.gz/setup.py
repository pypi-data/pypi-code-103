# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory',
 'understory.apps.micropub_server',
 'understory.apps.micropub_server.content',
 'understory.apps.micropub_server.content.templates',
 'understory.apps.micropub_server.media',
 'understory.apps.micropub_server.posts']

package_data = \
{'': ['*'],
 'understory.apps.micropub_server.media': ['templates/*'],
 'understory.apps.micropub_server.posts': ['templates/*']}

install_requires = \
['micropub>=0.0.4,<0.0.5', 'understory>=0,<1']

entry_points = \
{'web.apps': ['micropub_content = understory.apps.micropub_server.content:app',
              'micropub_media = understory.apps.micropub_server.media:app',
              'micropub_server = understory.apps.micropub_server.posts:app']}

setup_kwargs = {
    'name': 'understory-micropub-server',
    'version': '0.0.4',
    'description': 'A Micropub server for the Understory framework.',
    'long_description': '# understory-micropub-server\n\nA [Micropub][0] client for the [Understory][1] framework.\n\n[0]: https://micropub.spec.indieweb.org\n[1]: https://github.com/canopy/understory\n',
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
