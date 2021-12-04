# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['octopus_api']
install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'more-itertools>=8.11.0,<9.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['octopus = octopus:octopus']}

setup_kwargs = {
    'name': 'octopus-api',
    'version': '1.0.0',
    'description': "Octopus-api is a python library for performing client-based optimized concurrent requests and limit rates set by the endpoint contract. Octopus-api is simple; it combines the asyncio and aiohttp library's functionality and makes sure the requests follow the constraints set by the user.",
    'long_description': '# octopus-api\n![octopus_icon](https://github.com/FilipByren/octopus-api/blob/main/image.png?raw=true)\n## About\nOctopus-api is a python library for performing client-based optimized concurrent requests and limit rates set by the endpoint contract.\n\nOctopus-api is simple; it combines the [asyncio](https://docs.python.org/3/library/asyncio.html) and [aiohttp](https://docs.aiohttp.org/en/stable/) library\'s functionality and makes sure the requests follows the constraints set by the contract.\n\n## Installation\n`pip install octopus-api`\n\n## PyPi\nhttps://pypi.org/project/octopus-api/\n\n\n## Get started\nTo start Octopus, you first initiate the client, setting your constraints. \n```python\nclient = OctopusApi(rate=30, resolution="minute", retries=10)\nclient = OctopusApi(rate=5, resolution="sec", retries=3)\nclient = OctopusApi(concurrency=100, retries=5)\n```\nAfter that, you will specify what you want to perform on the endpoint response. This is done within a user-defined function.\n```python\nasync def patch_data(session: TentacleSession, request: Dict):\n    async with session.patch(url=request["url"], data=requests["data"], params=request["params"]) as response:\n        body = await response.json()\n        return body["id"]\n```\n\nAs Octopus `TentacleSession` uses [aiohttp](https://docs.aiohttp.org/en/stable/) under the hood, the resulting  way to write \n**POST**, **GET**, **PUT** and **PATCH** for aiohttp will be the same for octopus. The only difference is the added functionality of \nretries and rate limits (if set).\n\nFinally, you finish everything up with the `execute` call for the octopus client, where you provide the list of requests dicts your defined and the user function. The execute call will then return the waited list of returned values.\n\n```python\nresult: List = client.execute(requests_list=[\n    {\n        "url": "http://localhost:3000",\n        "data": {"id": "a", "first_name": "filip"},\n        "params": {"id": "a"}\n    },\n    {\n        "url": "http://localhost:3000",\n        "data": {"id": "b", "first_name": "morris"},\n        "params": {"id": "b"} \n    }\n    ] , func=patch_data)\n```\n\n\n### Examples\n\nOptimize the request based concurrency constraints:\n```python\nfrom octopus_api import TentacleSession, OctopusApi\nfrom typing import Dict, List\n\nif __name__ == \'__main__\':\n    async def get_text(session: TentacleSession, request: Dict):\n        async with session.get(url=request["url"], params=request["params"]) as response:\n            body = await response.text()\n            return body\n\n\n    client = OctopusApi(concurrency=100)\n    result: List = client.execute(requests_list=[{\n        "url": "http://google.com",\n        "params": {}}] * 100, func=get_text)\n    print(result)\n\n```\nOptimize the request based on rate limit constraints:\n```python\nfrom octopus_api import TentacleSession, OctopusApi\nfrom typing import Dict, List\n\nif __name__ == \'__main__\':\n    async def get_ethereum_id(session: TentacleSession, request: Dict):\n        async with session.get(url=request["url"], params=request["params"]) as response:\n            body = await response.json()\n            return body["id"]\n\n    client = OctopusApi(rate=30, resolution="minute")\n    result: List = client.execute(requests_list=[{\n        "url": "http://api.coingecko.com/api/v3/coins/ethereum?tickers=false&localization=false&market_data=false",\n        "params": {}}] * 100, func=get_ethereum_id)\n    print(result)\n\n```\n\n## Limitations\n1. Returned result from the user defined function comes in out of order.\n2. When setting rate-limiting, the api will not utilize the concurrency functionality and only run a single \noperation in sequence.\n',
    'author': 'Filip Byrén',
    'author_email': 'filip.j.byren@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FilipByren/octopus-api',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
