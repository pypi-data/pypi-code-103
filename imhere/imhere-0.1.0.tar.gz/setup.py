# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['imhere']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'imhere',
    'version': '0.1.0',
    'description': 'ImHere, simple log for simple debug',
    'long_description': '# ImHere\n### simple log for simple debug\n<br>\nImHere is an alternative of a simple print for debugging.\n\nReturn print with:\n\n- Timestamp\n- File name\n- Context (function or class)\n- Line of code\n- Variable mame\n- Variable value\n\n## Get started\n\n```python\nfrom imhere import ImHere\n\nimhere = ImHere()\n\ndef function():\n    variable = 97\n    imhere.log(variable)\n\n#[2021-11-26 19:44:50] test.py\\function\\line 6\\variable:97\n```\n\nChange default settings\n\n```python\nfrom imhere import ImHere, separator\n\nimhere = ImHere(\n   spr=separator.ARROW, \n   timestamp=True, \n   time_format="%y-%m-%d %H:%M:%S"\n)\n\ndef function():\n    variable = 97\n    imhere.log(variable)\n\n#[21-11-26 19:44:50] test.py->function->line 6->variable:97\n```\n\nSettings `separator`:\n\n```python\nSLASH = \'/\'\nBACKSLASH = \'\\\\\'\nPOINT = \'.\'\nVERTICAL_BAR = \'|\'\nHYPHEN = \'-\'\nUNDERSCORE = \'_\'\nARROW = \'->\'\n```\nTo disable the timestamp print, set `timestamp=False`\n\nTo change format timestamp, set `time_format=formatTimestamp`\n\n',
    'author': 'rojack96',
    'author_email': 'cerroberto96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
