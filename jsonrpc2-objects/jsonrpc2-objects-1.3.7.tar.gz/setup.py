# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jsonrpcobjects']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'jsonrpc2-objects',
    'version': '1.3.7',
    'description': 'A collection of objects for use in JSON-RPC 2.0 implementations.',
    'long_description': "[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# JSON-RPC 2.0 Objects\n\nA collection of objects for use in JSON-RPC 2.0 implementations.\n\n## Installation\n\n```shell\npip install jsonrpc2-objects\n```\n\n## Objects\n\nAvailable in `objects` are the following: \n\n| Object                   | Description                 |\n|--------------------------|-----------------------------|\n| RequestObjectParams      | Request with params         |\n| RequestObject            | Request without params      |\n| NotificationObjectParams | Notification with params    |\n| NotificationObject       | Notification without params |\n| ErrorResponseObject      | Response with result        |\n| ResultResponseObject     | Response with error         |\n\n## Errors\n\nPython exceptions are available for each JSON-RPC 2.0 error.\nEach error extends `JSONRPCError`.\n\nExample use with client:\n\n```python\nfrom jsonrpcobjects.errors import JSONRPCError, MethodNotFound\n\ntry:\n    client.example_method(params)\nexcept MethodNotFound:\n    print('Handle method not found')\nexcept JSONRPCError:\n    print('Handle any JSON RPC error.')\n```\n\n## JSON Types\n\nType hints are provided for the following JSON types.\n- JSONPrimitive\n- JSONArray\n- JSONObject\n- JSONStructured\n- JSON\n",
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/jsonrpc2-objects',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
