# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['snug']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1,<5'],
 'aiohttp': ['aiohttp>=3.4.4,<4.0.0'],
 'httpx': ['httpx>=0.21.1,<0.22.0'],
 'requests': ['requests>=2.20,<3.0']}

setup_kwargs = {
    'name': 'snug',
    'version': '2.3.0',
    'description': 'Write reusable web API interactions',
    'long_description': 'Snug 🧣\n=======\n\n.. image:: https://img.shields.io/pypi/v/snug.svg\n   :target: https://pypi.python.org/pypi/snug\n\n.. image:: https://img.shields.io/pypi/l/snug.svg\n   :target: https://pypi.python.org/pypi/snug\n\n.. image:: https://img.shields.io/pypi/pyversions/snug.svg\n   :target: https://pypi.python.org/pypi/snug\n\n.. image:: https://github.com/ariebovenberg/snug/actions/workflows/tests.yml/badge.svg\n   :target: https://github.com/ariebovenberg/snug\n\n.. image:: https://img.shields.io/codecov/c/github/ariebovenberg/snug.svg\n   :target: https://codecov.io/gh/ariebovenberg/snug\n\n.. image:: https://img.shields.io/readthedocs/snug.svg\n   :target: http://snug.readthedocs.io/\n\n.. image:: https://img.shields.io/codeclimate/maintainability/ariebovenberg/snug.svg\n   :target: https://codeclimate.com/github/ariebovenberg/snug/maintainability\n\n.. image:: https://img.shields.io/badge/dependabot-enabled-brightgreen.svg?longCache=true&logo=dependabot\n   :target: https://dependabot.com\n   \n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n\n\n**Snug** is a tiny toolkit for writing reusable interactions with web APIs. Key features:\n\n* Write once, run with different HTTP clients (sync *and* async)\n* Fits any API architecture (e.g. REST, RPC, GraphQL)\n* Simple, lightweight and versatile\n\nWhy?\n----\n\nWriting reusable web API interactions is difficult.\nConsider a generic example:\n\n.. code-block:: python\n\n    import json\n\n    def repo(name, owner):\n        """get a github repo by owner and name"""\n        request = Request(f\'https://api.github.com/repos/{owner}/{name}\')\n        response = my_http_client.send(request)\n        return json.loads(response.content)\n\nNice and simple. But...\n\n* What about async? Do we write another function for that?\n* How do we write clean unittests for this?\n* What if we want to use another HTTP client or session?\n* How do we use this with different credentials?\n\n*Snug* allows you to write API interactions\nindependent of HTTP client, credentials, or whether they are run (a)synchronously.\n\nIn contrast to most API client toolkits,\nsnug makes minimal assumptions and design decisions for you.\nIts simple, adaptable foundation ensures\nyou can focus on what makes your API unique.\nSnug fits in nicely whether you\'re writing a full-featured API wrapper,\nor just making a few API calls.\n\nQuickstart\n----------\n\n1. API interactions ("queries") are request/response generators.\n\n.. code-block:: python\n\n  import snug\n\n  def repo(name, owner):\n      """get a github repo by owner and name"""\n      request = snug.GET(f\'https://api.github.com/repos/{owner}/{name}\')\n      response = yield request\n      return json.loads(response.content)\n\n2. Queries can be executed:\n\n.. code-block:: python\n\n  >>> query = repo(\'Hello-World\', owner=\'octocat\')\n  >>> snug.execute(query)\n  {"description": "My first repository on Github!", ...}\n\nFeatures\n--------\n\n1. **Effortlessly async**. The same query can also be executed asynchronously:\n\n   .. code-block:: python\n\n      query = repo(\'Hello-World\', owner=\'octocat\')\n      repo = await snug.execute_async(query)\n\n2. **Flexibility**. Since queries are just generators,\n   customizing them requires no special glue-code.\n   For example: add validation logic, or use any serialization method:\n\n   .. code-block:: python\n\n     from my_types import User, UserSchema\n\n     def user(name: str) -> snug.Query[User]:\n         """lookup a user by their username"""\n         if len(name) == 0:\n             raise ValueError(\'username must have >0 characters\')\n         request = snug.GET(f\'https://api.github.com/users/{name}\')\n         response = yield request\n         return UserSchema().load(json.loads(response.content))\n\n3. **Pluggable clients**. Queries are fully agnostic of the HTTP client.\n   For example, to use `requests <http://docs.python-requests.org/>`_\n   instead of the standard library:\n\n   .. code-block:: python\n\n      import requests\n      query = repo(\'Hello-World\', owner=\'octocat\')\n      snug.execute(query, client=requests.Session())\n\n4. **Testability**. Queries can easily be run without touching the network.\n   No need for complex mocks or monkeypatching.\n\n   .. code-block:: python\n\n      >>> query = repo(\'Hello-World\', owner=\'octocat\')\n      >>> next(query).url.endswith(\'/repos/octocat/Hello-World\')\n      True\n      >>> query.send(snug.Response(200, b\'...\'))\n      StopIteration({"description": "My first repository on Github!", ...})\n\n5. **Swappable authentication**. Queries aren\'t tied to a session or credentials.\n   Use different credentials to execute the same query:\n\n   .. code-block:: python\n\n      def follow(name: str) -> snug.Query[bool]:\n          """follow another user"""\n          req = snug.PUT(\'https://api.github.com/user/following/{name}\')\n          return (yield req).status_code == 204\n\n      snug.execute(follow(\'octocat\'), auth=(\'me\', \'password\'))\n      snug.execute(follow(\'octocat\'), auth=(\'bob\', \'hunter2\'))\n\n6. **Related queries**. Use class-based queries to create an\n   expressive, chained API for related objects:\n\n   .. code-block:: python\n\n      class repo(snug.Query[dict]):\n          """a repo lookup by owner and name"""\n          def __init__(self, name, owner): ...\n\n          def __iter__(self): ...  # query for the repo itself\n\n          def issue(self, num: int) -> snug.Query[dict]:\n              """retrieve an issue in this repository by its number"""\n              r = snug.GET(f\'/repos/{self.owner}/{self.name}/issues/{num}\')\n              return json.loads((yield r).content)\n\n      my_issue = repo(\'Hello-World\', owner=\'octocat\').issue(348)\n      snug.execute(my_issue)\n\n7. **Pagination**. Define paginated queries for (asynchronous) iteration.\n\n   .. code-block:: python\n\n      def organizations(since: int=None):\n          """retrieve a page of organizations since a particular id"""\n          resp = yield snug.GET(\'https://api.github.com/organizations\',\n                                params={\'since\': since} if since else {})\n          orgs = json.loads(resp.content)\n          next_query = organizations(since=orgs[-1][\'id\'])\n          return snug.Page(orgs, next_query=next_query)\n\n      my_query = snug.paginated(organizations())\n\n      for orgs in snug.execute(my_query):\n          ...\n\n      # or, with async\n      async for orgs in snug.execute_async(my_query):\n          ...\n\n8. **Function- or class-based? You decide**.\n   One option to keep everything DRY is to use\n   class-based queries and inheritance:\n\n   .. code-block:: python\n\n      class BaseQuery(snug.Query):\n          """base github query"""\n\n          def prepare(self, request): ...  # add url prefix, headers, etc.\n\n          def __iter__(self):\n              """the base query routine"""\n              request = self.prepare(self.request)\n              return self.load(self.check_response((yield request)))\n\n          def check_response(self, result): ...  # raise nice errors\n\n      class repo(BaseQuery):\n          """get a repo by owner and name"""\n          def __init__(self, name, owner):\n              self.request = snug.GET(f\'/repos/{owner}/{name}\')\n\n          def load(self, response):\n              return my_repo_loader(response.content)\n\n      class follow(BaseQuery):\n          """follow another user"""\n          def __init__(self, name):\n              self.request = snug.PUT(f\'/user/following/{name}\')\n\n          def load(self, response):\n              return response.status_code == 204\n\n   Or, if you\'re comfortable with higher-order functions and decorators,\n   make use of `gentools <http://gentools.readthedocs.io/>`_\n   to modify query ``yield``, ``send``, and ``return`` values:\n\n   .. code-block:: python\n\n      from gentools import (map_return, map_yield, map_send,\n                            compose, oneyield)\n\n      class Repository: ...\n\n      def my_repo_loader(...): ...\n\n      def my_error_checker(...): ...\n\n      def my_request_preparer(...): ...  # add url prefix, headers, etc.\n\n      basic_interaction = compose(map_send(my_error_checker),\n                                  map_yield(my_request_preparer))\n\n      @map_return(my_repo_loader)\n      @basic_interaction\n      @oneyield\n      def repo(owner: str, name: str) -> snug.Query[Repository]:\n          """get a repo by owner and name"""\n          return snug.GET(f\'/repos/{owner}/{name}\')\n\n      @basic_interaction\n      def follow(name: str) -> snug.Query[bool]:\n          """follow another user"""\n          response = yield snug.PUT(f\'/user/following/{name}\')\n          return response.status_code == 204\n\n\nFor more info, check out the `tutorial <http://snug.readthedocs.io/en/latest/tutorial.html>`_,\n`advanced features <http://snug.readthedocs.io/en/latest/advanced.html>`_,\n`recipes <http://snug.readthedocs.io/en/latest/recipes.html>`_,\nor `examples <http://snug.readthedocs.io/en/latest/examples.html>`_.\n\n\nInstallation\n------------\n\nThere are no required dependencies. Installation is easy as:\n\n.. code-block:: bash\n\n   pip install snug\n\nAlthough snug includes basic sync and async HTTP clients,\nyou may wish to install `requests <http://docs.python-requests.org/>`_\nand/or `aiohttp <http://aiohttp.readthedocs.io/>`_.\n\n.. code-block:: bash\n\n   pip install requests aiohttp\n\n\nAlternatives\n------------\n\nIf you\'re looking for a less minimalistic API client toolkit,\ncheck out `uplink <http://uplink.readthedocs.io/>`_\nor `tapioca <http://tapioca-wrapper.readthedocs.io/>`_.\n',
    'author': 'Arie Bovenberg',
    'author_email': 'a.c.bovenberg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ariebovenberg/snug',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
