# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory',
 'understory.apps.indieauth_client',
 'understory.apps.indieauth_client.templates']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0,<1']

entry_points = \
{'web.apps': ['indieauth_client = understory.apps.indieauth_client:app']}

setup_kwargs = {
    'name': 'understory-indieauth-client',
    'version': '0.0.3',
    'description': 'An IndieAuth client for the Understory framework.',
    'long_description': '# understory-indieauth-client\n\nAn [IndieAuth][0] client for the [Understory][1] framework.\n\n[0]: https://indieauth.spec.indieweb.org\n[1]: https://github.com/canopy/understory\n',
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
