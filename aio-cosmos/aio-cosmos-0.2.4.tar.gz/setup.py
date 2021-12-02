# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aio_cosmos']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.0,<4.0.0']

setup_kwargs = {
    'name': 'aio-cosmos',
    'version': '0.2.4',
    'description': 'Ayncio Client for Azure Cosmos DB',
    'long_description': '# aio-cosmos\nAsyncio SDK for Azure Cosmos DB. This library is intended to be a very thin asyncio wrapper around the [Azure Comsos DB Rest API][1]. \nIt is not intended to have feature parity with the Microsoft Azure SDKs but to provide async versions of the most commonly used interfaces.\n\n[1]: (https://docs.microsoft.com/en-us/rest/api/cosmos-db/)\n\n## Feature Support\n### Databases\n✅ List\\\n✅ Create\\\n✅ Delete\n\n### Containers\n✅ Create\\\n✅ Delete\n\n### Documents\n✅ Create Single\\\n✅ Create Concurrent Multiple\\\n✅ Delete\\\n✅ Get\\\n✅ Query\n\n## Limitations\n\nThe library currently only supports Session level consistency, this may change in the future. \nFor concurrent writes the maximum concurrency level is based on a maximum of 100 concurrent\nconnections from the underlying aiohttp library. This may be exposed to the as a client \nsetting in a future version.\n\nSessions are managed automatically for document operations. The session token is returned in the\nresult so it is possible to manage sessions manually by providing this value in session_token to\nthe appropriate methods. This facilitates sending the token value back to an end client in a\nsession cookie so that writes and reads can maintain consistency across multiple instances of\nCosmos.\n\nThere is currently no retry policy on failed connections/broken connections and this must be entirely\nmanaged by the end user code. This may be implemented in the future\n\n## Installation\n\n```shell\npip install aio-cosmos\n```\n\n## Usage\n\n### Client Setup and Basic Usage\n\nThe client can be instantiated using either the context manager as below or directly using the CosmosClient class.\nIf using the CosmosClient class directly the user is responsible for calling the .connect() and .close() methods to\nensure the client is boot-strapped and resources released at the appropriate times.\n\n```python\nfrom aio_cosmos.client import get_client\n\nasync with get_client(endpoint, key) as client:\n    await client.create_database(\'database-name\')\n    await client.create_container(\'database-name\', \'container-name\', \'/partition_key_document_path\')\n    doc_id = str(uuid4())\n    res = await client.create_document(f\'database-name\', \'container-name\',\n                                       {\'id\': doc_id, \'partition_key_document_path\': \'Account-1\', \'description\': \'tax surcharge\'}, partition_key="Account-1")\n```\n\n### Querying Documents\n\nDocuments can be queried using the query_documents method on the client. This method returns an AsyncGenerator and should\nbe used in an async for statement as below. The generator automatically handles paging for large datasets. If you don\'t\nwish to iterate through the results use a list comprehension to collate all of them.\n\n```python\nasync for doc in client.query_documents(f\'database-name\', \'container-name\',\n                                        query="select * from r where r.account = \'Account-1\'",\n                                        partition_key="Account-1"):\n    print(f\'doc returned by query: {doc}\')\n```\n\n### Concurrent Writes / Multiple Documents\n\nThe client provides the ability to issue concurrent document writes using asyncio/aiohttp. Each document is represented\nby a tuple of (document, partition key value) as below.\n\n```python\ndocs = [\n    ({\'id\': str(uuid4()), \'account\': \'Account-1\', \'description\': \'invoice paid\'}, \'Account-1\'),\n    ({\'id\': str(uuid4()), \'account\': \'Account-1\', \'description\': \'VAT remitted\'}, \'Account-1\'),\n    ({\'id\': str(uuid4()), \'account\': \'Account-1\', \'description\': \'interest paid\'}, \'Account-1\'),\n    ({\'id\': str(uuid4()), \'account\': \'Account-2\', \'description\': \'annual fees\'}, \'Account-2\'),\n    ({\'id\': str(uuid4()), \'account\': \'Account-2\', \'description\': \'commission\'}, \'Account-2\'),\n]\n\nres = await client.create_documents(f\'database-name\', \'container-name\', docs)\n```\n\n### Results\n\nResults are returned in a dictionary with the following format:\n\n```python\n{\n    \'status\': str,\n    \'code\': int,\n    \'session_token\': Optional[str],\n    \'error\': Optional[str],\n    \'data\': Union[dict,list]\n}\n```\n- status will be either \'ok\' or \'failed\'\n- code is the integer HTTP response code\n- session_token is the string session code vector returned by Cosmos\n- error is a string error message to provide context to a failed status\n- data is the direct JSON response from Cosmos and will contain any error information in the case of failed operations\n\nNote, to see an error return in the above format you must pass ```raise_on_failure=False``` to the client constructor.\n',
    'author': 'Grant McDonald',
    'author_email': 'calmseasdev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/calmseas/aio-cosmos',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
