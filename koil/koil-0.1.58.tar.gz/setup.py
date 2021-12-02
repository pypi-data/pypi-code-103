# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['koil', 'koil.checker', 'koil.checker.defaults']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

extras_require = \
{'jupyter': ['jupyter>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'koil',
    'version': '0.1.58',
    'description': 'An abstract event loop to run in an async and sync context (especially jupyter and qt), with utility functions to allow both accesses',
    'long_description': '# Koil\n\n### Idea\n\nkoil\n\n\n \n### Prerequisites\n\nHerre only works with a running Oauth Instance (in your network or locally for debugging).\n\n### Usage\n\nIn order to initialize the Client you need to connect it as a Valid Application with your Arnheim Instance\n\n```python\nkoil = get_current_koil(group_name="default")\n```\n\nIn your following code you can simple query your data according to the Schema of the Datapoint\n\n```python\nfrom bergen.schema import Node\n\nnode = Node.objects.get(id=1)\nprint(node.name)\n\n```\n\n## Access Data from different Datapoints\n\nThe Arnheim Framework is able to provide data from different Data Endpoints through a commong GraphQL Interface\n. This allows you to access data from various different storage formats like Elements and Omero and interact without\nknowledge of their underlying api.\n\nEach Datapoint provides a typesafe schema. Arnheim Elements provides you with an implemtation of that schema.\n\n## Provide a Template for a Node\n\nDocumentation neccesary\n\n\n### Testing and Documentation\n\nSo far Bergen does only provide limitedunit-tests and is in desperate need of documentation,\nplease beware that you are using an Alpha-Version\n\n\n### Build with\n\n- [Arnheim](https://github.com/jhnnsrs/arnheim)\n- [Pydantic](https://github.com/jhnnsrs/arnheim)\n\n',
    'author': 'jhnnsrs',
    'author_email': 'jhnnsrs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
