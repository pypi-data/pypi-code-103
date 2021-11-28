# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sleepstudyparser', 'sleepstudyparser.constants', 'sleepstudyparser.objects']

package_data = \
{'': ['*'], 'sleepstudyparser': ['static/*']}

setup_kwargs = {
    'name': 'sleepstudyparser',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Sleep Study Parser\n\nSimple package which can be used to parse the sleep study report from Windows 11.\n\n## Usage\n\nBelow we are parsing a sleep study report where 12th state is like this:\n![img.png](sleepstudyparser/static/img.png)\n\nTo get the same thing via Python we can do this:\n\n```python\n>>> from sleepstudyparser.SleepStudyParser import SleepStudyParser\n>>> ssp = SleepStudyParser(number_of_days=2, report_name="DummySleepStudyReport", report_path=r"C:\\temp")\n>>> obj = ssp.parse()\n>>> len(obj.states)\n84\n>>> obj.states[11].start_time\n2021-11-15 07:16:48+00:00\n>>> obj.states[11].duration\n13:15:33\n>>> obj.states[11].state_type\nSessionType.SLEEP\n>>> obj.states[11].drips.sw_drips\n100\n>>> obj.states[11].drips.hw_drips\n68\n```',
    'author': 'debakarr',
    'author_email': 'debakar.roy@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Dibakarroy1997/sleepstudyparser',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
