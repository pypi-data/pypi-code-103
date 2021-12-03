# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['leetcode_runner', 'leetcode_runner.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'minilog>=2.0,<3.0']

entry_points = \
{'console_scripts': ['leetcode_runner = leetcode_runner.cli:main']}

setup_kwargs = {
    'name': 'leetcode-runner',
    'version': '0.0.2',
    'description': 'LeetCode solutions runner',
    'long_description': '# Overview\n\n⚠️ Work in progress\n\nLeetCode solutions runner\n\n[![PyPI Version](https://img.shields.io/pypi/v/leetcode-runner.svg)](https://pypi.org/project/leetcode-runner)\n[![PyPI License](https://img.shields.io/pypi/l/leetcode-runner.svg)](https://pypi.org/project/leetcode-runner)\n\n# Usage\n\n1. Install the library from PyPi\n2. Go to [LeetCode](https://leetcode.com) and pick a problem to solve\n3. Open your favourite IDE and import the `leetcode_runner`\n4. Copy a problem samples into some variable, like a `problem`, and copy the base `Solution` class that LeetCode provides\n5. `LeetCode(problem, Solution).check()` will run these samples!\n6. Pass your own samples into `check` function _(not implemented yet)_\n\n```py\nfrom leetcode_runner import LeetCode \nfrom typing import *\n\n# Copied as is from the LeetCode\nproblem = """\nExample 1:\n\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nOutput: Because nums[0] + nums[1] == 9, we return [0, 1].\nExample 2:\n\nInput: nums = [3,2,4], target = 6\nOutput: [1,2]\nExample 3:\n\nInput: nums = [3,3], target = 6\nOutput: [0,1]\n"""\n\nclass Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        return []\n\nLeetCode(problem, Solution).check()\n```\n\nWill print:\n\n```text\n----------\n[ FAILED ]\nnums = [2,7,11,15], target = 9\nExpected: [0, 1]\nActual  : []\n----------\n[ FAILED ]\nnums = [3,2,4], target = 6\nExpected: [1, 2]\nActual  : []\n----------\n[ FAILED ]\nnums = [3,3], target = 6\nExpected: [0, 1]\nActual  : []\n\n```\n\n# Setup\n\n## Requirements\n\n* Python 3.9+\n\n## Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install leetcode-runner\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add leetcode-runner\n```\n\n\n---\n\nThis project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-python](https://github.com/jacebrowning/template-python).\n',
    'author': 'fbjorn',
    'author_email': 'denis@fbjorn.cc',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/leetcode_runner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
