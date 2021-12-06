# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongox']

package_data = \
{'': ['*']}

install_requires = \
['motor>=2.4,<3.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'mongox',
    'version': '0.0.3',
    'description': 'Python Mongodb ODM using Motor and Pydantic',
    'long_description': '<p align="center">\n<a href="https://github.com/aminalaee/mongox">\n    <img width="420px" src="https://raw.githubusercontent.com/aminalaee/mongox/main/docs/assets/images/banner.png" alt"MongoX">\n</a>\n</p>\n\n<p align="center">\n<a href="https://github.com/aminalaee/mongox/actions">\n    <img src="https://github.com/aminalaee/mongox/workflows/Test%20Suite/badge.svg" alt="Build Status">\n</a>\n<a href="https://github.com/aminalaee/mongox/actions">\n    <img src="https://github.com/aminalaee/mongox/workflows/Publish/badge.svg" alt="Publish Status">\n</a>\n<a href="https://codecov.io/gh/aminalaee/mongox">\n    <img src="https://codecov.io/gh/aminalaee/mongox/branch/main/graph/badge.svg" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/mongox/">\n    <img src="https://badge.fury.io/py/mongox.svg" alt="Package version">\n</a>\n<a href="https://pypi.org/project/mongox" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/mongox.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n---\n\n# MongoX\n\nMongoX is an async python ODM (Object Document Mapper) for MongoDB\nwhich is built on top of [Motor][motor] and [Pydantic][pydantic].\n\nThe main features include:\n\n* Fully type annotated\n* Async support Python 3.7+ (since it\'s built on top of Motor)\n* Elegant editor support (since it\'s built on top of Pydantic)\n* Autocompletion everywhere, from object creation to query results\n* Custom query builder which is more intuitive and pythonic\n* 100% test coverage\n\nMongoX models are at the same time Pydantic models and have the same functionalitties,\nso you can use them with your existing Pydantic models.\n\n---\n\n**Documentation**: [https://aminalaee.github.io/mongox](https://aminalaee.github.io/mongox)\n\n---\n\n## Installation\n\n```shell\n$ pip install mongox\n```\n\n---\n\n## Quickstart\n\nYou can define `mongox` models the same way you define Pydantic models.\nThe difference is they should inherit from `mongox.Model` now:\n\n```python\nimport asyncio\n\nimport mongox\n\nclient = mongox.Client("mongodb://localhost:27017")\ndb = client.get_database("test_db")\n\n\nclass Movie(mongox.Model):\n    name: str\n    year: int\n\n    class Meta:\n        collection = db.get_collection("movies")\n```\n\nNow you can create some instances and insert them into the database:\n\n```python\nmovie = await Movie(name="Forrest Gump", year=1994).insert()\n```\n\nThe returned result will be a `Movie` instance, and `mypy`\nwill understand that this is a `Movie` instance.\nSo you will have type hints and validations everywhere:\n\n<img alt="MongoX insert screenshot" src="https://user-images.githubusercontent.com/19784933/141309006-94785d1b-c0de-4fde-8b7d-f59253657d64.png">\n\nNow you can fetch some data from the database.\n\nYou can use the same pattern as PyMongo/Motor:\n\n```python\nmovie = await Movie.query({"name": "Forrest Gump"}).get()\n```\n\nThe returned result will be a `Movie` instance, and `mypy`\nwill understand that this is a `Movie` instance.\n\nThis will have great IDE support, autocompletion and validation.\n\n<img alt="MongoX get screenshot" src="https://user-images.githubusercontent.com/19784933/141615279-f4534246-e09d-4d5e-90f6-32f0a3807769.png">\n\n\nOr you can use `Movie` fields instead of dictionaries in the query (less room for bugs):\n\n```python\nmovie = await Movie.query({Movie.name: "Forrest Gump"}).get()\n```\n\nAnd finally you can use a more intuitive query (limited yet):\n\n```python\nmovie = await Movie.query(Movie.name == "Forrest Gump").get()\n```\n\nNotice how we omitted the dictionary and passed the `Movie` fields in comparison.\n\n---\n\nPlease refer to the documentation [here](https://aminalaee.github.io/mongox) or the full examples [here](https://github.com/aminalaee/mongox/tree/main/examples).\n\n---\n\n[motor]: https://github.com/mongodb/motor\n[pydantic]: https://github.com/samuelcolvin/pydantic\n',
    'author': 'Amin Alaee',
    'author_email': 'mohammadamin.alaee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aminalaee/mongox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
