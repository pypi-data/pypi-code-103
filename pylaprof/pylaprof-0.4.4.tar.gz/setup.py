# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylaprof']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pylaprof-merge = scripts.merge:main']}

setup_kwargs = {
    'name': 'pylaprof',
    'version': '0.4.4',
    'description': 'A Python sampling profiler for AWS Lambda functions (and not only).',
    'long_description': "# pylaprof\npylaprof is a Python library that allows you to profile functions or sections of code.\n\nAs a decorator:\n```python\nfrom pylaprof import profile\n\n@profile()\ndef handler(event, context):\n  ...\n```\n\nAs a context manager:\n```python\nfrom pylaprof import Profiler\n\ndef main():\n  ...\n  with Profiler():\n    # Only code inside this context will be profiled.\n    ...\n```\n\nIt is built around three main abstractions: the *profiler*, the *sampler*, and\nthe *storer*.\n\nThe profiler is the main component of pylaprof, it takes care of taking\nsnapshots of your program's stack at regular intervals of times and feeding them\nto the *sampler* for processing; at the end of the profiling session, it will\nthen ask the *sampler* for a report and provide it to the *storer*.\n\nTake a look at the [source](./pylaprof/__init__.py) for more documentation and\nsome pre-implemented samplers and storers or [here](./examples) for some\nusage examples.\n\n## Features\n- Accessible: pylaprof's code is thoroughly documented and written to be read and\n  understood by other humans.\n\n- Extensible: you can write your own sampler or storer to generate reports in the format\n  you like and store them where and how you want.\n\n- Zero external dependencies[^1].\n\n- Close to zero impact on performances (check [benchmark](./benchmark) for\n  more details).\n\n- Reliable: pylaprof was built with the context of long-running\n  applications or continuously invoked lambda functions in mind.\n  It will never break your code or pollute your standard output or error\n  with unwanted messages.\n\n- Turn on/off profiling with an environment variable.\n\n- Store the profiling report only if execution takes longer than a threshold.\n\n[^1]: boto3 is optional and required only if you want to use the S3 storer.\n\n### pylaprof-merge\n`pylaprof-merge` is a simple CLI tool to merge multiple stackcollapse reports\ninto a single one. This might come in handy if you want to get an aggregated\noverview of a function or piece of code that is executed frequently for short\nperiods. It is installed automatically if you get pylaprof with pip.\n\n\n## Installation\n```\npip install pylaprof\n```\n\nOr just copy-paste the pylaprof directory where you need it.\n\n\n## Credits\n- This library is heavily inspired to [pprofile](\n  https://github.com/vpelletier/pprofile): thanks to its authors for writing such\n  accessible and well-documented code.\n- Thanks to @jvns for writing and distributing some of her *wizard zines* for free:\n  it's what got me into the rabbit hole of profiling in the first place.\n",
    'author': 'Giuseppe Lumia',
    'author_email': 'g.lumia@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/glumia/pylaprof',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
