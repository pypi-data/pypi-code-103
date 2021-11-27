# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['richerr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'richerr',
    'version': '0.2.3',
    'description': 'Rich errors (sort of)',
    'long_description': '# Welcome\n\n[![PyPI version](https://badge.fury.io/py/richerr.svg)](https://badge.fury.io/py/richerr)  [![codecov](https://codecov.io/gh/AdamBrianBright/python-richerr/branch/master/graph/badge.svg?token=DDBNKVLZWH)](https://codecov.io/gh/AdamBrianBright/python-richerr) [![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FAdamBrianBright%2Fpython-richerr.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FAdamBrianBright%2Fpython-richerr?ref=badge_shield)  \n\n## RichErr\n\nRichErr is a tiny module that gives you basic error class, which can be used in JSON, dict, list, and other mutation\n\n```python example.py\nfrom richerr import RichErr\n\nprint(RichErr.convert(ValueError(\'Hello world!\')).json(indent=2))\n```\n\n```json5\n{\n  "error": {\n    "code": 400,\n    "exception": "BadRequest",\n    "message": "Hello world!",\n    "caused_by": {\n      "error": {\n        "code": 500,\n        "exception": "ValueError",\n        "message": "Hello world!",\n        "caused_by": null\n      }\n    }\n  }\n}\n```\n\n## Installation\n\n### Poetry\n\n```shell\npoetry add RichErr\n```\n\n### PIP\n\n```shell\npip install RichErr\n```\n\n## Requirements\n\n- [x] Python 3.10+\n- [x] No package dependencies\n\n## Plugins\n\n- [x] Supported Django Validation and ObjectNotFound errors\n- [x] Supported DRF Validation errors\n- [x] Supported Pydantic Validation errors\n\n### Want to add your own error conversion?\n\nAdd direct conversion\n\n```python\nfrom richerr import RichErr, GatewayTimeout\n\n\nclass MyTimeoutError(IOError): ...\n\n\nRichErr.add_conversion(MyTimeoutError, GatewayTimeout)\n```\n\nOr add conversion method\n\n```python\nfrom richerr import RichErr\n\n\nclass MyTimeoutError(IOError): ...\n\n\ndef _convert(err: MyTimeoutError):\n    return RichErr.from_error(err, message=\'Something happened\', code=500, name=\'MyTimeoutError\')\n\n\nRichErr.add_conversion(MyTimeoutError, _convert)\n```\n\n!!!\nSubclasses will be checked before their parent, if multiple classes in same MRO will be registered.\n!!!\n\n [![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FAdamBrianBright%2Fpython-richerr.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FAdamBrianBright%2Fpython-richerr?ref=badge_large) ',
    'author': 'Bogdan Parfenov',
    'author_email': 'adam.brian.bright@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://adambrianbright.github.io/python-richerr/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10.0,<4.0',
}


setup(**setup_kwargs)
