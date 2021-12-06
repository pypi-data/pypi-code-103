# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['deadsimple']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deadsimple',
    'version': '0.1.3',
    'description': 'A dependency injection library, aimed for the least amount of magic',
    'long_description': '# deadsimple\n\n> A dependency injection library for python, aimed for the least amount of magic.\n\nHeavily influenced by [FastAPI]\'s dependency injection classes and logic.\n\n\nSimple Example\n\n```python\nfrom dataclasses import dataclass\nfrom deadsimple import Depends, resolve\n\n\n@dataclass\nclass DepA():\n    dep_b: DepB\n\n\n@dataclass\nclass DepB():\n    value: str\n\n\ndef get_dep_b() -> DepB:\n    return DepB(value="some val")\n\n\ndef get_dep_a(dep_b: DepB = Depends(get_dep_b)) -> DepA:\n    return DepA(dep_b=dep_b)\n\n\nmy_a = resolve(get_dep_a)\n\nassert my_a.dep_b.value == "some val"\n```\n\n\nDependencies will instantiate once per factory for each call to `resolve`.\n\n```python\n@dataclass\nclass DepC():\n    dep_a: DepA\n    dep_b: DepB\n\n\ndef get_dep_c(\n    dep_a: DepA = Depends(get_dep_a),\n    dep_b: DepB = Depends(get_dep_b),\n) -> DepC:\n\n    return DepC(dep_a=dep_a, dep_b=dep_b)\n\n\nmy_c = resolve(get_dep_c)\n\nassert my_c.dep_b is my_c.dep_a.dep_b\n```\n\n\nFor Singleton use [lru_cache] or [cache] from [functools]\n\n```python\nfrom functools import lru_cache\n# or from functools import cache if you\'re 3.9+\n\n\n@dataclass\nclass Singleton():\n    pass\n\n\n@dataclass\nclass NotSingleton():\n    singleton_dep: Singleton\n\n\n@lru_cache\ndef get_singleton() -> Singleton:\n    return Singleton()\n\n\ndef get_not_singleton(singleton: Singleton = Depends(get_singleton)) -> NotSingleton:\n    return NotSingleton(singleton_dep=singleton)\n\n\nnot_singleton_a = resolve(get_not_singleton)\nnot_singleton_b = resolve(get_not_singleton)\n\nassert not_singleton_a is not not_singleton_b\nassert not_singleton_a.singleton_dep is not_singleton_b.singleton_dep\n```\n\nOverride dependencies:\n\n```python\noverride_dep_b = DepB(value="some other val")\n\nmy_a = resolve(get_dep_a, overrides={get_dep_b: override_dep_b})\n\nassert my_a.dep_b.value == "some other val"\n```\n\n## Installing\n\n```\npip install deadsimple\n```\n\n\n[FastAPI]: https://github.com/tiangolo/fastapi\n[lru_cache]: https://docs.python.org/3/library/functools.html#functools.lru_cache\n[cache]: https://docs.python.org/3/library/functools.html#functools.cache\n[functools]: https://docs.python.org/3/library/functools.html\n',
    'author': 'Nitzan Zada',
    'author_email': 'nitzan.zada@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mastern2k3/deadsimple',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
