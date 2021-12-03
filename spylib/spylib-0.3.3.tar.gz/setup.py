# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spylib', 'spylib.oauth', 'spylib.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'fastapi>=0.65.1,<0.66.0',
 'httpx>=0.18.1,<0.19.0',
 'loguru>=0.5.3,<0.6.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'shortuuid>=1.0.1,<2.0.0',
 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'spylib',
    'version': '0.3.3',
    'description': "A library to facilitate interfacing with Shopify's API",
    'long_description': '# Shopify Python Library - SPyLib\n\nThe Shopify python library or SPyLib, simplifies the use of the Shopify\nservices such as the REST and GraphQL APIs as well as the OAuth authentication.\nAll of this is done **asynchronously using asyncio**.\n\n## Installation\n\n```bash\npip install spylib\n```\n\n## Contributing\n\nIf you want to contribute a small change/feature, the best is to just create a PR with\nyour changes.\nFor bigger changes/features it\'s best to open an issue first and discuss it to agree\non the code organization and overall implementation before spending too much time on\nthe code, unless you want to keep it in your own forked repo.\n\n### Setting up the development environment\n\nWe use the [python poetry](https://python-poetry.org/) package to manage this package.\nFollow the official instructions to install poetry on your system then once you clone\nthis repository just just need to do the following to install the dependencies from\nthe development environment, as well as install `spylib` in\n[editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable):\n```bash\npoetry install\n```\n\nThen you can start monitoring the code for changes and run the test suite this way:\n```bash\npoetry shell\nscripts/test_watch.sh\n```\n\n\n## Overview\n\n### Token\n\nThe token class contains the majority of the logic for communicating with shopify.\nTo use the token class, you must define a child class for the tokens you are using \nand implement the `save` and `load` abstract methods. Your option for child classes \nare `OnlineTokenABC` or `OfflineTokenABC`:\n\n#### Implement Token Classes \n\n```python\nclass OfflineToken(OfflineTokenABC):\n  async def save(self):\n      # Some code to save the token to a database\n\n  @classmethod\n  async def load(cls, store_name: str):\n      # Some code to load the token from the database\n\nclass OnlineToken(OnlineTokenABC):\n  async def save(self):\n      # Some code to save the token to a database\n\n  @classmethod\n  async def load(cls, store_name: str, user_id: str):\n      # Some code to load the token from the database\n```\n\n#### Create Token\n\nOnce you have defined these methods, we can create an instance of a token using\none of the following:\n\n```python\ntoken = OfflineToken(\n  store_name,\n  access_token,\n  scope\n)\n\ntoken = OnlineToken(\n  store_name,\n  access_token,\n  scope,\n  expires_in,\n  associated_user_scope,\n  associated_user_id\n)\n```\n\n#### Querying Shopify\n\nWe can query the store using either the REST endpoint or the GraphQL endpoint:\n\n```python\ntoken.execute_rest(\n  goodstatus,\n  method,\n  debug,\n  endpoint\n)\n\ntoken.execute_gql(\n  query,\n  variables,\n  operation_name\n)\n```\n\nThe `REST` method takes a `goodstatus` parameter that is the response from the API\nthat will not trigger an error.\n\nThe `method` can be `get`, `post`, `put` or `delete`.\n\nDebug is the error that is outputted on failure.\n\nEndpoint is the API endpoint string that we are querying.\n\n### OAuth\n\nRather than reimplementing for each app the\n[Shopify OAuth authentication](https://shopify.dev/tutorials/authenticate-with-oauth)\none can simple get a [FastAPI](https://fastapi.tiangolo.com/) router that provides\nthe install and callback endpoints ready to handle the whole OAuth process.\nYou just need to call `init_oauth_router` such that:\n\n```python\nfrom spylib.oauth import OfflineToken, OnlineToken, init_oauth_router\n\n\nasync def my_post_install(storename: str, offline_token: OfflineToken):\n    """Function handling the offline token obtained at the end of the installation"""\n    # Store to database\n    pass\n\nasync def my_post_login(storename: str, online_token: OnlineToken):\n    """Function handling the online token obtained at the end of the user login"""\n    # Store to database\n    pass\n\noauth_router = init_oauth_router(\n    app_scopes=[\'write_orders\', \'write_products\'],\n    user_scopes=[\'read_orders\', \'write_products\'],\n    public_domain=\'my.app.com\',\n    private_key=\'KEY_FOR_OAUTH_JWT\',\n    post_install=my_post_install,\n    post_login=my_post_login,\n)\n```\n\nThe `app_scopes` are for the offline token and the `user_scopes` for the online token.\nThe `public_domain` is used to set the callback URL used in the OAuth process.\n\nThis library uses a JWT encoded `nonce` to avoid the need for a database or some other\nmechanism to track the `nonce`. This JWT has an expiration time and is unique for each\nOAuth process making it a valid `nonce` mechanism.\nThe `private_key` parameter defines the key used to encode and decode this JWT.\n\nThe `post_install` and `post_login` provide a way to inject functions handling the\nresult of the installation and the login processes respectivaly. They are meant in \nparticular to record the offline and online tokens in your app\'s database.\nThey can be synchronous or asynchronous functions taking the storename and the token\nas arguments.\n```\n',
    'author': 'Anthony Hillairet',
    'author_email': 'ant@satel.ca',
    'maintainer': 'Anthony Hillairet',
    'maintainer_email': 'ant@satel.ca',
    'url': 'https://github.com/SatelCreative/satel-spylib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
