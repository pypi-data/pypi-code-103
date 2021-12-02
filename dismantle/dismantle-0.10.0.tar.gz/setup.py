# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dismantle',
 'dismantle.extension',
 'dismantle.index',
 'dismantle.package',
 'dismantle.plugin']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['dismantle = dismantle.cli:main']}

setup_kwargs = {
    'name': 'dismantle',
    'version': '0.10.0',
    'description': 'Python package / plugin / extension manager',
    'long_description': '# Dismantle\n\n**Dismantle** Python package / plugin / extension manager.\n\n```python\n"""Simple plugin example"""\nfrom dismantle import plugin\n\n\nclass Chat():\n    @plugin.register(\'chat.message\')\n    def show(self, message):\n        print(message)\n\n\n@plugin.plugin(\'chat.message\', order=-1)\ndef make_uppercase(message):\n    return message.upper()\n\n```\n\n```python\n"""Full example using all aspects."""\nfrom pathlib import Path\nfrom dismantle.extension import Extensions, IExtension\nfrom dismantle.index import JsonFileIndexHandler\nfrom dismantle.package import LocalPackageHandler\n\n\nclass ColorExtension(IExtension):\n    _category = \'color\'\n\n    def color(self) -> None:\n        ...\n\n\nclass GreenColorExtension(ColorExtension):\n    _name = \'green\'\n\n    def color(self) -> None:\n        print(f\'color is {self._name}\')\n\n\npackages = {}\nindex = JsonFileIndexHandler(\'index.json\')\nfor pkg_meta in index:\n    meta = index[pkg_meta]\n    path = datadir.join(meta[\'path\'])\n    package = LocalPackageHandler(meta[\'name\'], path)\n    package._meta = {**package._meta, **meta}\n    package.install()\n    packages[package.name] = package\nextensions = Extensions([ColorExtension], packages, \'ext_\')\nassert extensions.types == [\'color\']\nassert list(extensions.category(\'color\').keys()) == [\n    \'@scope-one/package-one.extension.green.GreenColorExtension\',\n    \'@scope-one/package-two.extension.red.RedColorExtension\',\n    \'@scope-one/package-three.extension.blue.BlueColorExtension\',\n]\nassert list(extensions.extensions.keys()) == [\'color\']\nassert list(extensions.imports.keys()) == [\n    \'@scope-one/package-one.extension.green\',\n    \'@scope-one/package-two.extension.red\',\n    \'@scope-one/package-three.extension.blue\'\n]\n```\n\nDismantle allows you to provide the ability to create a plugin/extension/module for an application.\nIt does this by checking a package index and using that index to manage package versions. Packages\nthen contain plugins (using decorators) and extensions (using a custom module loader) to add the\nadditional functionality to the application.\n\n## Installing Dismantle and Supported Versions\n\nDismantle is available on PyPI:\n\n```console\n$ python -m pip install dismantle\n```\n\nDismantle officially supports Python 3.7+.\n\n## Supported Features & Best–Practices\n\nDismantle is ready for the demands of providing flexibility within applications allowing developers\nto build rich ecosystems around core applications.\n\n### Index Management\n\n- easy to create custom index handlers providing additional ways to define package indexes\n- local index file support using json\n- url based index file support using json\n- etag based caching for url based index\n\n### Packaging\n\n- easy to create custom package handlers providing additional ways to define package sources\n- easy to create custom package formats compression types and structures\n- support for zip, tar.gz, tgz, and local directories as package formats\n- support for local and url based (http/https) package handlers\n- hash validation for packages with the ability to verify package integrity\n\n### Extensions\n\n- Categorized extension groups to filter extension types (eg. loggers, parsers, ...)\n- Support for __init__ or .py based module loading.\n- Extension activation and deactivation management.\n- Module name collision avoidance\n- Hierarchical module naming\n\n### Plugins\n\n- Decorator based plugins with pre and post value modification\n- Multiple plugins per function with ability to set execution order\n- Activation management\n',
    'author': 'Area28 Technologies',
    'author_email': 'dev@area28.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/area28technologies/dismantle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
