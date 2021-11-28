# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['config_injector']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0', 'pyaml>=20.4.0,<21.0.0', 'toml>=0.10.2,<0.11.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=0.12,<=4']}

setup_kwargs = {
    'name': 'config-injector',
    'version': '0.3.0',
    'description': 'Simple dependency injection framework for python for easy and logical app configuration.',
    'long_description': '# config-injector\nConfig-injector is a very simple framework which aims to do only two things: (1) define configurable functions and (2) inject configuration data into those functions at runtime.\n\n## Installation\nInstall with pip.\n```bash\npip install config-injector\n```\n\n## Getting Started\nAnnotate any callable as a configurable function using `@config`. Note that the `@config` decorator requires that you provide callable functions for each argument. These callable functions should return the expected type. The object is to break all arguments down to fundamental types: string, integer, float or dictionary.\n\n```python\nfrom collections import namedtuple\nfrom typing import Text, Dict, SupportsInt\nfrom pathlib import Path\n\nfrom config_injector import config, Injector\n\n\nMockThing0 = namedtuple("MockThing0", ["arg_1", "arg_2", "arg_3", "arg_4"])\n\n@config(arg_1=str, arg_2=str, arg_3=str, arg_4=str)\ndef mock_thing_0(arg_1: Text, arg_2: Text, arg_3: Text, arg_4: Text):\n    return MockThing0(arg_1, arg_2, arg_3, arg_4)\n\n\n@config(arg_5=int, arg_6=int, arg_7=int, arg_8=int)\ndef mock_thing_1(arg_5, arg_6, arg_7, arg_8):\n    return {"key_a": arg_5, "key_b": arg_6, "key_c": arg_7, "key_d": arg_8}\n\n@config(t0=mock_thing_0, t1=mock_thing_1, arg_9=str)\ndef mock_things(t0: MockThing0, t1: Dict[SupportsInt], arg_9: Text):\n    return (t0, t1, arg_9)\n\ndef get_things(config_file=Path("config.json")):\n    injector = Injector()\n    injector.load_file(config_file)\n    return injector["things"].instantiate(mock_things)\n```\n\nNow that the configurable functions are annotated, we can write a configuration for them.\n\n```json\n{\n  "things": {\n    "t0": {"arg_1": "a", "arg_2": "b", "arg_3": "c", "arg_4": "d"},\n    "t1": {"arg_5": 1, "arg_6": 2, "arg_7": 3, "arg_8": 4},\n    "arg_9": "e"\n  }\n}\n```\n\nThis configuration file can be loaded in the runtime portion of our implementation using `get_things()` to instantiate the configured objects created by our functions.\n\n### Polymorphism\nIt is common to want to determine the implementation at runtime. This can be accomplished by delaring the class of an argument as a tuple of multiple types.\n\n```python\nfrom config_injector import config, Injector\n\nclass BaseClass:...\n\nclass ImplementationA(BaseClass):...\n\nclass ImplementationB(BaseClass):...\n\n@config()\ndef implementation_a():\n    return ImplementationA()\n\n@config()\ndef implementation_b():\n    return ImplementationB()\n\n@config(t0=(implementation_a, implementation_b))\ndef mock_thing(t0):\n    return {\n        "t0": t0\n    }\n\n# Instantiate using implementation a.\nmock_thing_using_a = Injector({"t0": {"type": "implementation_a"}}).instantiate(mock_thing)\n# Instantiate using implementation b.\nmock_thing_using_b = Injector({"t0": {"type": "implementation_b"}}).instantiate(mock_thing)\n```\n\n### Environment Variable Interpolation\nConfigurations can contain environment variables for any value. Variables shall be placed within braces `${VAR_NAME}` and use only letters and underscores. For example, for the following configuration, the environment variables would be interpolated.\n\n```python\n{\n    "db": {\n         "url": "${DB_URL}",\n         "user": "${DB_USER}",\n         "password": "${DB_PASSWORD}",\n    }\n}\n```',
    'author': 'DustinMoriarty',
    'author_email': 'dustin.moriarty@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DustinMoriarty/config-injector',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
