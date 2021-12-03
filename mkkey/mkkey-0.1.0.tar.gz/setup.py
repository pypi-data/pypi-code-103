# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkkey']

package_data = \
{'': ['*']}

install_requires = \
['click-help-colors>=0.9.1,<0.10.0',
 'click>=8.0.3,<9.0.0',
 'cryptography>=36.0.0,<37.0.0',
 'pyseto>=1.5.0,<2.0.0',
 'shellingham>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['mkkey = mkkey.cli:cli']}

setup_kwargs = {
    'name': 'mkkey',
    'version': '0.1.0',
    'description': 'A Generic Application-Layer Key Generator supporting JWK and PASERK.',
    'long_description': '# mkkey - An Application-Layer Key Generator supporting JWK and PASERK.\n\n[![PyPI version](https://badge.fury.io/py/mkkey.svg)](https://badge.fury.io/py/mkkey)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkkey)\n![Github CI](https://github.com/dajiaji/mkkey/actions/workflows/python-package.yml/badge.svg)\n[![codecov](https://codecov.io/gh/dajiaji/mkkey/branch/main/graph/badge.svg?token=QN8GXEYEP3)](https://codecov.io/gh/dajiaji/mkkey)\n\nmkkey is a CLI tool for generating following application-layer keys:\n- [JWK (JSON Web Key) - RFC7517](https://datatracker.ietf.org/doc/html/rfc7517)\n- [PASERK (Platform-Agnositc Serialized Keys)](https://github.com/paseto-standard/paserk)\n\n\nYou can install mkkey with pip:\n\n```sh\n$ pip install mkkey\n```\n\nAnd then, you can use it as follows.\n\n\nFor JWK:\n\n```sh\n$ mkkey jwk ec\n{\n    "public": {\n        "jwk": {\n            "kty": "EC",\n            "crv": "P-256",\n            "x": "Ti-mNoi-uQFYBVNkH6BSmuTAd8WL8kyEVJufZYv3mG8",\n            "y": "ANwoZQFI_teNrltM0s9LPjWli0_zyYvvv8cEZWKx1CQ"\n        }\n    },\n    "secret": {\n        "jwk": {\n            "kty": "EC",\n            "crv": "P-256",\n            "x": "Ti-mNoi-uQFYBVNkH6BSmuTAd8WL8kyEVJufZYv3mG8",\n            "y": "ANwoZQFI_teNrltM0s9LPjWli0_zyYvvv8cEZWKx1CQ",\n            "d": "l9Pbq0BmCsOzdapBtSxVpRiHhDTK5-ATteA0nMKzvFU"\n        }\n    }\n}\n```\n\nFor PASERK:\n\n```sh\n$ mkkey paserk v4 public\n{\n    "public": {\n        "paserk": "k4.public.2BWUTPg5pmXZ3EVrOBv9I4I_F8Afj0TJ21HkaPT926M"\n    },\n    "secret": {\n        "paserk": "k4.secret.fKIawV2PPVpEONDcEH3_p1dc4OEYlTncmMa8gvwMVy_YFZRM-DmmZdncRWs4G_0jgj8XwB-PRMnbUeRo9P3bow"\n    }\n}\n\n```\n\nSee help for details:\n\n```sh\n$ mkkey --help\n$ mkkey jwk --help\n$ mkkey paserk --help\n```\n',
    'author': 'Ajitomi Daisuke',
    'author_email': 'dajiaji@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dajiaji/mkkey',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
