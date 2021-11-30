# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['demo', 'docs', 'tests', 'tests_grammar', 'ts2python']

package_data = \
{'': ['*']}

modules = \
['ts2pythonParser']
install_requires = \
['DHParser>=0.9.9,<0.10.0']

entry_points = \
{'console_scripts': ['ts2python = ts2pythonParser:main']}

setup_kwargs = {
    'name': 'ts2python',
    'version': '0.5',
    'description': 'Python-Interoperability for Typescript-Interfaces',
    'long_description': '# ts2python\n\nPython-interoperability for Typescript-Interfaces.\nTranspiles TypeScript-Interface-definitions to Python \nTypedDicts, plus support for run-time type-checking \nof JSON-data.\n\n## License\n\nts2python is open source software under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0)\n\nCopyright 2021 Eckhart Arnold <arnold@badw.de>, Bavarian Academy of Sciences and Humanities\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n    https://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n\n## Purpose\n\nWhen processing JSON data, as for example form a \n[JSON-RPC](https://www.jsonrpc.org/) call, with Python, it would\nbe helpful to have Python-definitions of the JSON-structures at\nhand, in order to solicit IDE-Support, static type checking and,\npotentially to enable structural validation at runtime. \n\nThere exist different technologies for defining the structure of\nJSON-data. Next to [JSON-schema](http://json-schema.org/), a \nde facto very popular technology for defining JSON-obejcts are\n[Typescript-Interfaces](https://www.typescriptlang.org/docs/handbook/2/objects.html). \nFor example, the \n[language server protocol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/) \ndefines the structure of the JSON-data exchanged between client \nand server with Typescript-Interfaces.\n\nIn order to enable structural validation on the Python-side, \nts2python transpiles the typescript-interface definitions\nto Python-data structure definitions, primarily, \n[TypedDicts](https://www.python.org/dev/peps/pep-0589/),\nbut with some postprocessing it can also be adjusted to\nother popular models for records or data structures in\nPython, e.g.\n[pydantic](https://pydantic-docs.helpmanual.io/)-Classes\nand the like.\n\n## Installation\n\nts2python can be installed from the command line with the command:\n\n    # pip install ts2python\n\nts2python requires the parsing-expression-grammar-framwork \n[DHParser](https://gitlab.lrz.de/badw-it/DHParser)\nwhich will automatically be installed as a dependency by \nthe `pip`-command. ts2python requires at least Python Version 3.8\nto run. (If there is any interest, I might backport it to Python 3.6.)\nHowever, the Python-code it produces is backwards compatible \ndown to Python 3.6, if the \n[typing extensions](https://pypi.org/project/typing-extensions/) \nhave been installed.\n\nFor a demonstration how the TypeScript-Interfaces are transpiled\nto Python-code, run the `demo.sh`-script (or `demo.bat` on Windows)\nin the "demo"-sub-directory or the ts2python-directory. \nOr, run the `tst_ts2python_gramm.py` in the ts2python-directory\nand look up the grammar-test-reports in the "REPORT"-sub-directory \nof the "test_grammar"-subdirectory.\n\n\n## Usage\n\nIn order to generate TypedDict-classes from Typescript-Interfaces,\nrun `ts2python` on the Typescript-Interface definitions:\n\n    # ts2python interfaces.ts\n\nThis generates a .py-file in same directory as the source\nfile that contains the TypedDict-classes and can simpy be \nimported in Python-Code:\n\n    >>> from interface_definitions import *\n\nOther data-representation models than TypedDict can be supported\nwith the `--base` and `--decorator`-options, e.g.\n\n    >>> ts2python --base pydantic.BaseModel interfaces.ts\n\nor:\n\n    >>> ts2python --decorator attr.s interfaces.ts\n\n*Presently, ts2python does only offer very rudimentary support\nfor other models than TypedDict. So, before it can be used, \nfurther adjustments to the generated file are necessary when\nusing data models other than TypedDict.*\n\n\n## Validation\n\nts2python ships support for runtime-type validation. While type\nerrors can be detected by static type checkers, runtime type \nvalidation can be useful when processing data from an outside\nsource which cannot statically be checked, like, for example,\njson-data stemming from an RPC-call. ts2python runtime-type\nvalidation can be invoked via dedicated functions or via\ndecorator as in this example:\n\n    from ts2python.json_validation import TypedDict, type_check\n\n    class Position(TypedDict, total=True):\n        line: int\n        character: int \n\n    class Range(TypedDict, total=True):\n        start: Position\n        end: Position\n\n    @type_check\n    def middle_line(rng: Range) -> Position:\n        line = (rng[\'start\'][\'line\'] + rng[\'end\'][\'line\']) // 2\n        character = 0\n        return Position(line=line, character=character)\n\n    data = {\'start\': {\'line\': 1, \'character\': 1},\n           \'end\': {\'line\': 8, \'character\': 17}}\n    assert middle_line(data) == {\'line\': 4, \'character\': 0}\n\n    malformed_data = {\'start\': 1, \'end\': 8}\n    middle_line(malformed_data)  # <- TypeError raised by @type_check \n\nWith the type decorator the last call fails with a TypeError:\n\n    TypeError: Parameter "rng" of function "middle_line" failed the type-check, because:\n    Type error(s) in dictionary of type <class \'__main__.Range\'>:\n    Field start: \'1\' is not of <class \'__main__.Position\'>, but of type <class \'int\'>\n    Field end: \'8\' is not of <class \'__main__.Position\'>, but of type <class \'int\'>\n\nBoth the call and the return types can be validated.\n',
    'author': 'Eckhart Arnold',
    'author_email': 'eckhart.arnold@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jecki/ts2python',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
