# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['charmonium', 'charmonium.freeze']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'charmonium.freeze',
    'version': '0.4.1',
    'description': '',
    'long_description': '=================\ncharmonium.freeze\n=================\n\n.. image: https://img.shields.io/pypi/dm/charmonium.freeze\n   :alt: PyPI Downloads\n.. image: https://img.shields.io/pypi/l/charmonium.freeze\n   :alt: PyPI Downloads\n.. image: https://img.shields.io/pypi/pyversions/charmonium.freeze\n   :alt: Python versions\n.. image: https://img.shields.io/github/stars/charmoniumQ/charmonium.freeze?style=social\n   :alt: GitHub stars\n.. image: https://img.shields.io/librariesio/sourcerank/pypi/charmonium.freeze\n   :alt: libraries.io sourcerank\n\n- `PyPI`_\n- `GitHub`_\n\nInjectively, deterministically maps objects to hashable, immutable objects.\n\n``frozenset`` is to ``set`` as ``freeze`` is to ``Any``.\n\nThat is, ``type(a) is type(b) and a != b`` implies ``freeze(a) != freeze(b)``.\n\nMoreover, this function is deterministic, so it can be used to compare\nstates **across subsequent process invocations** (with the same\ninterpreter major and minor version).\n\n>>> obj = [1, 2, 3, {4, 5, 6}, object()]\n>>> hash(obj)\nTraceback (most recent call last):\n  File "<stdin>", line 1, in <module>\nTypeError: unhashable type: \'list\'\n\n>>> from charmonium.freeze import freeze\n>>> frozen_obj = freeze(obj)\n>>> frozen_obj\n(1, 2, 3, frozenset({4, 5, 6}), (((\'__newobj__\', (\'cls\', \'args\'), (None,), b\'...\'), (), ()), (\'object\',)))\n>>> hash(frozen_obj) % 1\n0\n\n-------------\nSpecial cases\n-------------\n\n- ``freeze`` on functions returns their bytecode, constants, and\n  closure-vars. This means that ``freeze_state(f) == freeze_state(g)`` implies\n  ``f(x) == g(x)``. The remarkable thing is that this is true across subsequent\n  invocations of the same process. If the user edits the script and changes the\n  function, then it\'s ``freeze_state`` will change too.\n\n- ``freeze`` on objects returns the objects that would be used by `pickle`_ from\n  ``__reduce__``, ``__reduce_ex__``, ``__getnewargs__``, ``__getnewargs_ex__``,\n  and ``__getstate__``. The simplest of these to customize your object\n  ``__gestate__``. See the `pickle`_ documentation for details.\n\n- In the cases where ``__getstate__`` is already defined for pickle, and this\n  definition is not suitable for ``freeze_state``, one may override this with\n  ``__getfrozenstate__`` which takes precedence.\n\nAlthough, this function is not infallible for user-defined types; I will do my\nbest, but sometimes these laws will be violated. These cases include:\n\n- Cases where ``__eq__`` makes objects equal despite differing attributes or\n  inversely make objects inequal despite equal attributes.\n\n   - This can be mitigated if ``__getstate__`` or ``__getfrozenstate__``\n\n.. _`PyPI`: https://pypi.org/project/charmonium.freeze/\n.. _`GitHub`: https://github.com/charmoniumQ/charmonium.freeze\n.. _`pickle`: https://docs.python.org/3/library/pickle.html#pickling-class-instances\n',
    'author': 'Samuel Grayson',
    'author_email': 'grayson5@illinois.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/charmoniumQ/charmonium.freeze.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
