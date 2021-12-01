# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indieauth']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0,<1']

setup_kwargs = {
    'name': 'indieauth',
    'version': '0.0.5',
    'description': 'A library for writing IndieAuth servers and clients.',
    'long_description': '# indieauth-python\n\nA library for writing [IndieAuth][0] servers and clients.\n\n> IndieAuth is an identity layer on top of OAuth 2.0 [RFC6749], primarily\n> used to obtain an OAuth 2.0 Bearer Token [RFC6750] for use by [Micropub]\n> clients. End-Users and Clients are all represented by URLs. IndieAuth\n> enables Clients to verify the identity of an End-User, as well as to\n> obtain an access token that can be used to access resources under the\n> control of the End-User.\n\n[0]: https://indieauth.spec.indieweb.org\n',
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
