# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytailer']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pytailer',
    'version': '0.1.0',
    'description': 'It is very simple implementation of the unix shell utility `tail`',
    'long_description': '# PyTAILer\n\nPyTAILer is very simple implementation of the unix shell utility `tail`.\n\n```python\nfrom pytailer import fail_tail\n\nwith fail_tail("some_file.txt", lines=10) as tail:\n    for line in tail:  # be careful: infinite loop!\n        print(line)\n```\n\nOf course, you can use async version:\n\n```python\nimport asyncio\n\nfrom pytailer import async_fail_tail\n\n\nasync def main():\n    with async_fail_tail("some_file.txt", lines=10) as tail:\n        async for line in tail:  # be careful: infinite loop!\n            print(line)\n\n\nasyncio.run(main())  # python 3.7+ \n```\n',
    'author': 'Andrey Lemets',
    'author_email': 'a.a.lemets@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/EnotYoyo/pytailer',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
