# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['btypes']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions==4.0.1']

setup_kwargs = {
    'name': 'btypes',
    'version': '4.0.1dev0',
    'description': 'Aliases with correct capitalization for built-in Python types.',
    'long_description': '# btypes\n\n> Aliases with correct capitalization for built-in Python types.\n\n[PEP8](https://www.python.org/dev/peps/pep-0008/#class-names) states that classes should have names in CamelCase.\nHowever, all the built-in types are lower case: `str`, `bool`, `int`, `float`, `list`, `dict`, etc.\nThis library provides aliases for all these types that are capitalized correctly.\nThey are straightforward aliases and can be used exactly like the original types.\n\n## Install\n\nRequires Python 3.9+.\n\n```\npip install btypes\n```\n\n## Examples\n\n```python\nfrom btypes import Int, List, Str\n\ndef comma_list(lst: List[Int]) -> Str:\n    return ", ".join(Str(e) for e in lst)\n\ndef range_list(limit: Int) -> List[Int]:\n    return List(range(limit))\n```\n\nAlso works with pattern matching:\n```python\nfrom btypes import Bool, Str, Union\n\ndef print_type(x: Union[Bool, Str]) -> None:\n    match x:\n        case Bool():\n            print("a boolean")\n        case Str():\n            print("a string")\n```\n',
    'author': 'Thomas M',
    'author_email': 'thomas5max@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/thomkeh/btypes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
