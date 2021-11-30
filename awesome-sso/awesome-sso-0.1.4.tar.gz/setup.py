# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['awesome_sso', 'awesome_sso.exceptions', 'awesome_sso.store']

package_data = \
{'': ['*']}

install_requires = \
['autoflake>=1.4,<2.0',
 'coveralls>=3.3.1,<4.0.0',
 'minio>=7.1.1,<8.0.0',
 'odmantic>=0.3.5,<0.4.0']

setup_kwargs = {
    'name': 'awesome-sso',
    'version': '0.1.4',
    'description': 'sso general utility for services connected to sso',
    'long_description': '[![Stable Version](https://img.shields.io/pypi/v/awesome-sso?label=stable)](https://pypi.org/project/awesome-sso/)\n[![tests](https://github.com/MoBagel/awesome-sso/workflows/ci/badge.svg)](https://github.com/MoBagel/awesome-sso)\n[![Coverage Status](https://coveralls.io/repos/github/MoBagel/awesome-sso/badge.svg?branch=develop)](https://coveralls.io/github/MoBagel/awesome-sso)\n\n# Awesome SSO\n\nA library designed to host common components for a cluster of microservices sharing a single sign on.\n\n## Feature\n\n- [x] A common exception class, supporting both status code and custom error code to map\n  to more detailed error message or serve as i18n key.\n\n## Usage\n\n### Installation\n1. `pip install awesome-sso`\n\n### Exceptions\nUsing fast API as example, we may simply throw exception with a proper status code, and an optional error code.\nWe may also supply arbitrary key value in args dict, to help frontend render better error message.\n```python\nfrom awesome_sso.exceptions import NotFound\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\'/transactions\')\ndef get(id: str):\n  try:\n    obj = find_by_id(id)\n  except Exception as e:\n    raise NotFound(message=\'transaction not found\' % id, error_code=\'A0001\', args={id: id})\n  ...\n```\nAnd we may implement a common error handler to convert all these errors to proper response schema\n```python\nfrom awesome_sso.exceptions import HTTPException\nfrom fastapi.requests import Request\nfrom fastapi.responses import JSONResponse\n\n@app.exception_handler(HTTPException)\nasync def http_exception_handler(request: Request, exc: HTTPException):\n  return JSONResponse(\n    status_code=exc.status_code,\n    content={\n      \'detail\': exc.detail,\n      \'error_code\': exc.error_code,\n    }\n  )\n```\n\nThis would result in a response with status code 404, and body\n\n```json\n{\n  "status_code": 404,\n  "detail": {\n    "message": "transaction not found",\n    "id": "some_id",\n  },\n  "error_code": "A0001"\n}\n```\nWith this response, frontend can decide to simply render detail, or map it to detailed message.\nIf error_code "A0001" correspond to the following i18 n entry\n```json\n"error.A0001": {"en-US": "transaction can not be found with supplied {id}: {message}"}\n```\nwe may format message accordingly with\n```typescript\nerrorMessage = formatMessage({ id: `error.${error.data.error_code}` }, error.data.detail);\n```\n\nNote that error code is not supplied, is default to status code. So it is always safe to simply use error_code in frontend\nto decide what to render.\n\n### Data Store\n#### Minio\nrefer to `tests/test_minio.py`\n#### Mongo\n```python\nfrom awesome_sso.store.mongo import MongoDB\n\ndb = MongoDB(\n        host=MONGODB_HOST,\n        port=MONGODB_PORT,\n        username=MONGODB_USERNAME,\n        password=MONGODB_PASSWORD,\n        database=MONGODB_DB,\n)\ndb.engine.save(some_odmantic_model)\ndb.engine.get(SomeOdmanticModel, query string)\n```\nrefer to [odmantic document](https://art049.github.io/odmantic/engine/) on how \nto use odmantic engine.\n\n## Development\n\n### Installing Poetry\n1. create your own environment for poetry, and simply run: `pip install poetry`\n2. alternatively, you can refer to [poetry\'s official page](https://github.com/python-poetry/poetry)\n3. to be able to use `poe` directly, `pip install poethepoet`\n\n### Contributing\n1. project setup: `poetry install`\n2. create your own branch to start developing new feature.\n3. before creating pr, make sure you pass `poe lint` and `./run_test.sh`.\n   - what happened inside `./run_test.sh` is that a minio server is setup for you\n     temporarily, and teardown and unit test is finished.\n   - notice that `poe test` would also work if you already have a minio up and running. You need\n    the following env variable: `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_ADDRESS` upon running `poe test`.\n4. for a list of available poe command, `poe`\n5. after you submit a pr, you should check if pipeline is successful.\n\n### Releasing\n1. update version in `pyproject.toml`.\n2. merge to master, and a release pipeline will be triggered. A package with version specified in `pyproject.toml`\n  will be pushed to pypi.\n',
    'author': 'Schwannden Kuo',
    'author_email': 'schwannden@mobagel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MoBagel/awesome-sso',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
