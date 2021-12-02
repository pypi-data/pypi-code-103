# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fds', 'fds.sdk', 'fds.sdk.utils', 'fds.sdk.utils.authentication']

package_data = \
{'': ['*']}

install_requires = \
['oauthlib>=3.1.1,<4.0.0',
 'python-jose>=3.3.0,<4.0.0',
 'requests-oauthlib>=1.3.0,<2.0.0',
 'requests>=2.25.1,<3.0.0']

setup_kwargs = {
    'name': 'fds.sdk.utils',
    'version': '0.9.0',
    'description': 'Utilities for interacting with FactSet APIs.',
    'long_description': '<img alt="FactSet" src="https://www.factset.com/hubfs/Assets/images/factset-logo.svg" height="56" width="290">\n\n# FactSet SDK Utilities for Python\n\n[![PyPi](https://img.shields.io/pypi/v/fds.sdk.util)](https://pypi.org/project/fds.sdk.util/)\n[![Apache-2 license](https://img.shields.io/badge/license-Apache2-brightgreen.svg)](https://www.apache.org/licenses/LICENSE-2.0)\n\nThis repository contains a collection of utilities that supports FactSet\'s SDK in Python and facilitate usage of FactSet APIs.\n\n## Installation\n\n### Poetry\n\n```python\npoetry add fds.sdk.utils\n```\n\n### pip\n\n```python\npip install fds.sdk.utils\n```\n\n## Usage\n\nThis library contains multiple modules, sample usage of each module is below.\n\n### Authentication\n\nFirst, you need to create the OAuth 2.0 client configuration that will be used to authenticate against FactSet\'s APIs:\n\n1. Create a [new application](https://developer.factset.com/applications) on FactSet\'s Developer Portal.\n2. When prompted, download the configuration file and move it to your development environment.\n\n```python\nfrom fds.sdk.utils.authentication import ConfidentialClient\nimport requests\n\nclient = ConfidentialClient(\'/path/to/config.json\')\nres = requests.get(\n  \'https://api.factset.com/analytics/lookups/v3/currencies\',\n  headers={\n    \'Authorization\': \'Bearer \' + client.get_access_token()\n  })\n\nprint(res.text)\n```\n\n## Modules\n\nInformation about the various utility modules contained in this library can be found below.\n\n### Authentication\n\nThe [authentication module](src/fds/sdk/utils/authentication) provides helper classes that facilitate [OAuth 2.0](https://github.com/factset/oauth2-guidelines) authentication and authorization with FactSet\'s APIs. Currently the module has support for the [client credentials flow](https://github.com/factset/oauth2-guidelines#client-credentials-flow-1).\n\nEach helper class in the module has the following features:\n\n* Accepts a configuration file or `dict` that contains information about the OAuth 2.0 client, including the client ID and private key.\n* Performs authentication with FactSet\'s OAuth 2.0 authorization server and retrieves an access token.\n* Caches the access token for reuse and requests a new access token as needed when one expires.\n\n#### Configuration\n\nClasses in the authentication module require OAuth 2.0 client configuration information to be passed to constructors through a JSON-formatted file or a `dict`. In either case the format is the same:\n\n```json\n{\n    "name": "Application name registered with FactSet\'s Developer Portal",\n    "clientId": "OAuth 2.0 Client ID registered with FactSet\'s Developer Portal",\n    "clientAuthType": "Confidential",\n    "owners": ["USERNAME-SERIAL"],\n    "jwk": {\n        "kty": "RSA",\n        "use": "sig",\n        "alg": "RS256",\n        "kid": "Key ID",\n        "d": "ECC Private Key",\n        "n": "Modulus",\n        "e": "Exponent",\n        "p": "First Prime Factor",\n        "q": "Second Prime Factor",\n        "dp": "First Factor CRT Exponent",\n        "dq": "Second Factor CRT Exponent",\n        "qi": "First CRT Coefficient",\n    }\n}\n```\n\nIf you\'re just starting out, you can visit FactSet\'s Developer Portal to [create a new application](https://developer.factset.com/applications) and download a configuration file in this format.\n\nIf you\'re creating and managing your signing key pair yourself, see the required [JWK parameters](https://github.com/factset/oauth2-guidelines#jwk-parameters) for public-private key pairs.\n\n## Debugging\n\nThis library uses the [logging module](https://docs.python.org/3/howto/logging.html) to log various messages that will help you understand what it\'s doing. You can increase the log level to see additional debug information using standard conventions. For example:\n\n```python\nlogging.getLogger(\'fds.sdk.utils\').setLevel(logging.DEBUG)\n```\n\nor\n\n```python\nlogging.getLogger(\'fds.sdk.utils.authentication\').setLevel(logging.DEBUG)\n```\n\n# Contributing\n\nPlease refer to the [contributing guide](CONTRIBUTING.md).\n\n# Copyright\n\nCopyright 2021 FactSet Research Systems Inc\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n',
    'author': 'FactSet Research Systems',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://developer.factset.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
