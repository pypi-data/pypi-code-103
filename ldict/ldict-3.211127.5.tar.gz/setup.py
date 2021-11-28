# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ldict', 'ldict.core', 'ldict.parameter']

package_data = \
{'': ['*']}

install_requires = \
['lange>=0.2101.24,<0.2102.0', 'uncompyle6>=3.7.4,<4.0.0']

extras_require = \
{'full': ['pandas>=1.3.3,<2.0.0', 'dill>=0.3.4,<0.4.0']}

setup_kwargs = {
    'name': 'ldict',
    'version': '3.211127.5',
    'description': 'Lazy dict',
    'long_description': '![test](https://github.com/davips/ldict/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/davips/ldict/branch/main/graph/badge.svg)](https://codecov.io/gh/davips/ldict)\n<a href="https://pypi.org/project/ldict">\n<img src="https://img.shields.io/pypi/v/ldict.svg?label=release&color=blue&style=flat-square" alt="pypi">\n</a>\n![Python version](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue.svg)\n[![license: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n\n<!--- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5501845.svg)](https://doi.org/10.5281/zenodo.5501845) --->\n[![arXiv](https://img.shields.io/badge/arXiv-2109.06028-b31b1b.svg?style=flat-square)](https://arxiv.org/abs/2109.06028)\n[![API documentation](https://img.shields.io/badge/doc-API%20%28auto%29-a0a0a0.svg)](https://davips.github.io/ldict)\n\n# ldict\n\nA lazy `dict`.\n\n[Latest release](https://pypi.org/project/ldict) |\n[Current code](https://github.com/davips/ldict) |\n[API documentation](https://davips.github.io/ldict)\n\n## See also\n\n* laziness+identity+persistence ([idict](https://pypi.org/project/idict))\n\n## Overview\n\nA `ldict` is a `dict` with `str` keys.\n\n**Simple usage example**\n<details>\n<p>\n\n```python3\nfrom ldict import ldict\n\na = ldict(x=3)\nprint(a)\n"""\n{\n    "x": 3\n}\n"""\n```\n\n```python3\n\nb = ldict(y=5)\nprint(b)\n"""\n{\n    "y": 5\n}\n"""\n```\n\n```python3\n\nprint(a >> b)\n"""\n{\n    "x": 3,\n    "y": 5\n}\n"""\n```\n\n\n</p>\n</details>\n\nWe consider that every value is generated by a process, starting from an `empty` ldict. The process is a sequence of\ntransformation steps done through the operator `>>`, which symbolizes a data flow. There are two types of steps:\n\n* **value insertion** - represented by dict-like objects\n* **function application** - represented by ordinary python functions\n\nA `ldict` is completely defined by its key-value pairs so that\nit can be converted from/to a built-in dict.\n\nCreating a ldict is not different from creating an ordinary dict. Optionally it can be created through the `>>` operator\nused after `empty`:\n![img.png](https://raw.githubusercontent.com/davips/ldict/main/examples/img.png)\n\nFunction application is done in the same way. The parameter names define the input fields, while the keys in the\nreturned dict define the output fields:\n![img_1.png](https://raw.githubusercontent.com/davips/ldict/main/examples/img_1.png)\n\nSimilarly, for anonymous functions:\n![img_5.png](https://raw.githubusercontent.com/davips/ldict/main/examples/img_5.png)\n\nFinally, the result is only evaluated at request:\n![img_6.png](https://raw.githubusercontent.com/davips/ldict/main/examples/img_6.png)\n\n\n## Installation\n### ...as a standalone lib\n```bash\n# Set up a virtualenv. \npython3 -m venv venv\nsource venv/bin/activate\n\n# Install from PyPI...\npip install --upgrade pip\npip install -U ldict\npip install -U ldict[full]  # use this for extra functionality (recommended)\n\n# ...or, install from updated source code.\npip install git+https://github.com/davips/ldict\n```\n\n### ...from source\n```bash\ngit clone https://github.com/davips/ldict\ncd ldict\npoetry install\n```\n\n## Examples\n**Merging two ldicts**\n<details>\n<p>\n\n```python3\nfrom ldict import ldict\n\na = ldict(x=3)\nprint(a)\n"""\n{\n    "x": 3\n}\n"""\n```\n\n```python3\n\nb = ldict(y=5)\nprint(b)\n"""\n{\n    "y": 5\n}\n"""\n```\n\n```python3\n\nprint(a >> b)\n"""\n{\n    "x": 3,\n    "y": 5\n}\n"""\n```\n\n\n</p>\n</details>\n\n**Lazily applying functions to ldict**\n<details>\n<p>\n\n```python3\nfrom ldict import ldict\n\na = ldict(x=3)\nprint(a)\n"""\n{\n    "x": 3\n}\n"""\n```\n\n```python3\n\na = a >> ldict(y=5) >> {"z": 7} >> (lambda x, y, z: {"r": x ** y // z})\nprint(a)\n"""\n{\n    "x": 3,\n    "y": 5,\n    "z": 7,\n    "r": "→(x y z)"\n}\n"""\n```\n\n```python3\n\nprint(a.r)\n"""\n34\n"""\n```\n\n```python3\n\nprint(a)\n"""\n{\n    "x": 3,\n    "y": 5,\n    "z": 7,\n    "r": 34\n}\n"""\n```\n\n\n</p>\n</details>\n\n**Parameterized functions and sampling**\n<details>\n<p>\n\n```python3\nfrom random import Random\n\nfrom ldict import empty, let\n\n\n# A function provide input fields and, optionally, parameters.\n# For instance:\n# \'a\' is sampled from an arithmetic progression\n# \'b\' is sampled from a geometric progression\n# Here, the syntax for default parameter values is borrowed with a new meaning.\ndef fun(x, y, a=[-100, -99, -98, ..., 100], b=[0.0001, 0.001, 0.01, ..., 100000000]):\n    return {"z": a * x + b * y}\n\n\ndef simplefun(x, y):\n    return {"z": x * y}\n\n\n# Creating an empty ldict. Alternatively: d = ldict().\nd = empty >> {}\nprint(d)\n"""\n{}\n"""\n```\n\n```python3\n\n# Putting some values. Alternatively: d = ldict(x=5, y=7).\nd["x"] = 5\nd["y"] = 7\nprint(d)\n"""\n{\n    "x": 5,\n    "y": 7\n}\n"""\n```\n\n```python3\n\n# Parameter values are uniformly sampled.\nd1 = d >> simplefun\nprint(d1)\nprint(d1.z)\n"""\n{\n    "x": 5,\n    "y": 7,\n    "z": "→(x y)"\n}\n35\n"""\n```\n\n```python3\n\nd2 = d >> simplefun\nprint(d2)\nprint(d2.z)\n"""\n{\n    "x": 5,\n    "y": 7,\n    "z": "→(x y)"\n}\n35\n"""\n```\n\n```python3\n\n# Parameter values can also be manually set.\ne = d >> let(fun, a=5, b=10)\nprint(e.z)\n"""\n95\n"""\n```\n\n```python3\n\n# Not all parameters need to be set.\ne = d >> Random() >> let(fun, a=5)\nprint("e =", e.z)\n"""\ne = 700025.0\n"""\n```\n\n```python3\n\n# Each run will be a different sample for the missing parameters.\ne = e >> Random() >> let(fun, a=5)\nprint("e =", e.z)\n"""\ne = 32.0\n"""\n```\n\n```python3\n\n# We can define the initial state of the random sampler.\n# It will be in effect from its location place onwards in the expression.\ne = d >> Random(0) >> let(fun, a=5)\nprint(e.z)\n"""\n725.0\n"""\n```\n\n```python3\n\n# All runs will yield the same result,\n# if starting from the same random number generator seed.\ne = e >> Random(0) >> let(fun, a=[555, 777])\nprint("Let \'a\' be a list:", e.z)\n"""\nLet \'a\' be a list: 700003885.0\n"""\n```\n\n```python3\n\n# Reproducible different runs are achievable by using a single random number generator.\ne = e >> Random(0) >> let(fun, a=[5, 25, 125, ..., 10000])\nprint("Let \'a\' be a geometric progression:", e.z)\n"""\nLet \'a\' be a geometric progression: 700003125.0\n"""\n```\n\n```python3\nrnd = Random(0)\ne = d >> rnd >> let(fun, a=5)\nprint(e.z)\ne = d >> rnd >> let(fun, a=5)  # Alternative syntax.\nprint(e.z)\n"""\n725.0\n700000025.0\n"""\n```\n\n```python3\n\n# Output fields can be defined dynamically through parameter values.\n# Input fields can be defined dynamically through kwargs.\ncopy = lambda source=None, target=None, **kwargs: {target: kwargs[source]}\nd = empty >> {"x": 5}\nd >>= let(copy, source="x", target="y")\nprint(d)\nd.evaluate()\nprint(d)\n\n"""\n{\n    "x": 5,\n    "y": "→(source target x)"\n}\n{\n    "x": 5,\n    "y": 5\n}\n"""\n```\n\n\n</p>\n</details>\n\n**Composition of sets of functions**\n<details>\n<p>\n\n```python3\nfrom random import Random\n\nfrom ldict import empty\n\n\n# A multistep process can be defined without applying its functions\n\n\ndef g(x, y, a=[1, 2, 3, ..., 10], b=[0.00001, 0.0001, 0.001, ..., 100000]):\n    return {"z": a * x + b * y}\n\n\ndef h(z, c=[1, 2, 3]):\n    return {"z": c * z}\n\n\n# In the ldict framework \'data is function\',\n# so the alias ø represents the \'empty data object\' and the \'reflexive function\' at the same time.\n# In other words: \'inserting nothing\' has the same effect as \'doing nothing\'.\nfun = empty >> g >> h  # empty enable the cartesian product of the subsequent sets of functions within the expression.\nprint(fun)\n"""\n«λ{} × λ»\n"""\n```\n\n```python3\n\n# An unnapplied function has its free parameters unsampled.\n# A compostition of functions results in an ordered set (Cartesian product of sets).\n# It is a set because the parameter values of the functions are still undefined.\nd = {"x": 5, "y": 7} >> (Random(0) >> fun)\nprint(d)\n"""\n{\n    "x": 5,\n    "y": 7,\n    "z": "→(c z→(a b x y))"\n}\n"""\n```\n\n```python3\n\nprint(d.z)\n"""\n105.0\n"""\n```\n\n```python3\n\nd = {"x": 5, "y": 7} >> (Random(0) >> fun)\nprint(d.z)\n"""\n105.0\n"""\n```\n\n```python3\n\n# Reproducible different runs by passing a stateful random number generator.\nrnd = Random(0)\ne = d >> rnd >> fun\nprint(e.z)\n"""\n105.0\n"""\n```\n\n```python3\n\ne = d >> rnd >> fun\nprint(e.z)\n"""\n14050.0\n"""\n```\n\n```python3\n\n# Repeating the same results.\nrnd = Random(0)\ne = d >> rnd >> fun\nprint(e.z)\n"""\n105.0\n"""\n```\n\n```python3\n\ne = d >> rnd >> fun\nprint(e.z)\n"""\n14050.0\n"""\n```\n\n\n</p>\n</details>\n\n<!--- ## Persistence\nExtra dependencies can be installed to support saving data to disk or to a server in the network. \n\n**[still an ongoing work...]**\n\n`poetry install -E full`\n--->\n\n## Concept\n\nA ldict is like a common Python dict, with extra functionality and lazy. It is a mapping between string keys, called\nfields, and any serializable (pickable protocol=5) object.\n\n## Grants\nThis work was partially supported by Fapesp under supervision of\nProf. André C. P. L. F. de Carvalho at CEPID-CeMEAI (Grants 2013/07375-0 – 2019/01735-0).\n',
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
