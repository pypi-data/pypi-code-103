# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ecas']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'click>=8.0.1,<9.0.0',
 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['ecas = ecas.ecas:list_ecas_steps']}

setup_kwargs = {
    'name': 'ecas',
    'version': '0.3.3',
    'description': 'A CLI to directly read your PR status',
    'long_description': '# Ecas RP automation script\nThis tool has been written to check the status of your PR application in ECAS automatically. This avoid multiple click and form filling. You can set alert using a system like cron.\n\n## Getting started\n### From PyPI\n```bash\npip3 install ecas\n```\n### From Source\n1. Get poetry\n\nOn Linux & MacOS\n```bash\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -\n```\nOn Windows with powershell\n```\n(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -\n```\n2. Get the code\n```bash\ngit clone git@github.com:pievalentin/ecas.git && cd ecas\n```\n3. Build it\n```bash\npoetry build\n```\nThe previous command will create a dist folder. Now run:\n```\npip3 install dist/ecas*.whl\n```\nRestart your terminal so that `ecas` is available.\n## Usage\n\n```bash\necas lastname iuc_number birthday birth_country_code\n```\n\nFor example for France:\n```bash\necas Dupont 112245589 "2001-01-31" 022\n```\nExample of output:\n```\nYour status is: InProcess\n\nThe detail of your process is:\n- We received your application for permanent residence  on December 10, 2020.\n- We sent you correspondence acknowledging receipt of your application(s) on October 22, 2021.\n- We started processing your application on October 22, 2021.\n- We sent you correspondence on October 22, 2021. If you have not yet provided the information or the requested documents, please do so as soon as possible.  \nPlease wait until you receive the correspondence before sending us additional information, as the correspondence will outline all information that is required.\n- We sent you medical instructions on November 25, 2021. To avoid delays, please provide us the information requested in the letter as soon as possible.  \nPlease consider delays in mail delivery before contacting us.\n```\n\nWhen everything was verified by ircc, your status will change to `DecisionMade` \n\nFor more details, you can\n```bash\necas --help\n```\n## Find your country code\n\nTo find your country code, you can look it up [in this file](/country_code.csv)\n\n## NB\nUse this tool responsibly. Don\'t spam IRCC server :)\n',
    'author': 'Pierre Valentin',
    'author_email': 'pievalentin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pievalentin/ecas',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
