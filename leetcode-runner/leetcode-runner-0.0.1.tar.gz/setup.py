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
    'version': '0.0.1',
    'description': 'LeetCode solutions runner',
    'long_description': '# Overview\n\n⚠️ Work in progress\n\nLeetCode solutions runner\n\nThis project was generated with [cookiecutter](https://github.com/audreyr/cookiecutter) using [jacebrowning/template-python](https://github.com/jacebrowning/template-python).\n\n[![Coverage Status](https://img.shields.io/codecov/c/gh/fbjorn/leetcode-runner)](https://codecov.io/gh/fbjorn/leetcode-runner)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/fbjorn/leetcode-runner.svg)](https://scrutinizer-ci.com/g/fbjorn/leetcode-runner)\n[![PyPI Version](https://img.shields.io/pypi/v/leetcode_runner.svg)](https://pypi.org/project/leetcode_runner)\n[![PyPI License](https://img.shields.io/pypi/l/leetcode_runner.svg)](https://pypi.org/project/leetcode_runner)\n\n# Setup\n\n## Requirements\n\n* Python 3.9+\n\n## Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install leetcode_runner\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add leetcode_runner\n```\n\n# Usage\n\nAfter installation, the package can imported:\n\n```py\nfrom leetcode_runner import LeetCode \nfrom typing import *\n\n# Copied as is from the LeetCode\nproblem = """\nExample 1:\n\nInput: nums = [2,7,11,15], target = 9\nOutput: [0,1]\nOutput: Because nums[0] + nums[1] == 9, we return [0, 1].\nExample 2:\n\nInput: nums = [3,2,4], target = 6\nOutput: [1,2]\nExample 3:\n\nInput: nums = [3,3], target = 6\nOutput: [0,1]\n"""\n\nclass Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        return []\n\nLeetCode(problem, Solution).check()\n```\n\nWill print:\n\n```text\n----------\n[ FAILED ]\nnums = [2,7,11,15], target = 9\nExpected: [0, 1]\nActual  : []\n----------\n[ FAILED ]\nnums = [3,2,4], target = 6\nExpected: [1, 2]\nActual  : []\n----------\n[ FAILED ]\nnums = [3,3], target = 6\nExpected: [0, 1]\nActual  : []\n\n```\n',
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
