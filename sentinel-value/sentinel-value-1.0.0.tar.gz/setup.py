# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sentinel_value']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sentinel-value',
    'version': '1.0.0',
    'description': 'Sentinel Values - unique objects akin to None, True, False',
    'long_description': 'sentinel-value\n==============\n\n|pypi badge| |build badge| |docs badge|\n\n\n``sentinel-value`` is a Python package, that helps to create `Sentinel Values`_ -\nspecial singleton objects, akin to ``None``, ``NotImplemented`` and  ``Ellipsis``.\n\nIt implements the ``sentinel()`` function (described by `PEP 661`_),\nand for advanced cases it also provides the ``SentinelValue()`` class (not a part of `PEP 661`_).\n\n.. _`Sentinel Values`: https://en.wikipedia.org/wiki/Sentinel_value\n.. _`PEP 661`: https://www.python.org/dev/peps/pep-0661\n\n\nUsage example:\n\n.. code:: python\n\n  from sentinel_value import sentinel\n\n  MISSING = sentinel("MISSING")\n\n  def get_something(default=MISSING):\n      ...\n      if default is not MISSING:\n          return default\n      ...\n\n\nOr, the same thing, but using the ``SentinelValue`` class\n(slightly more verbose, but allows to have nice type annotations):\n\n.. code:: python\n\n  from typing import Union\n  from sentinel_value import SentinelValue\n\n  class Missing(SentinelValue):\n      pass\n\n  MISSING = Missing(__name__, "MISSING")\n\n  def get_something(default: Union[str, Missing] = MISSING):\n      ...\n      if default is not MISSING:\n          return default\n      ...\n\n\nLinks\n-----\n\n- Read the Docs: https://sentinel-value.readthedocs.io\n- GitHub repository: https://github.com/vdmit11/sentinel-value\n- Python package: https://pypi.org/project/sentinel-value/\n\n\n.. |pypi badge| image:: https://img.shields.io/pypi/v/sentinel-value.svg\n  :target: https://pypi.org/project/sentinel-value/\n  :alt: Python package version\n\n.. |build badge| image:: https://github.com/vdmit11/sentinel-value/actions/workflows/build.yml/badge.svg\n  :target: https://github.com/vdmit11/sentinel-value/actions/workflows/build.yml\n  :alt: Tests Status\n\n.. |docs badge| image:: https://readthedocs.org/projects/sentinel-value/badge/?version=latest\n  :target: https://sentinel-value.readthedocs.io/en/latest/?badge=latest\n  :alt: Documentation Status\n\n',
    'author': 'Dmitry Vasilyanov',
    'author_email': 'vdmit11@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vdmit11/sentinel-value',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.0,<4.0.0',
}


setup(**setup_kwargs)
