# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['md_redact']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'md-redact',
    'version': '0.2.0',
    'description': 'Redact portions of content if a condition is met',
    'long_description': '# Markdown Redact\nAn extremely simple markdown extension that will optionally redact content from\na document.\n\n# Installation\nThis extension is designed for [python-markdown](https://python-markdown.github.io/).\n\n`pip install markdown md-redact`\n\n# Usage\nIn your environment:\n\n```shell\nexport MD_REDACT_CONTENT=1\n```\n\nIn your markdown document:\n\n```markdown\nThis is $some sensitive content$ in a markdown document.\n```\n\nIn your Python code:\n\n```python\nimport markdown\n\n\nwith open("filename.md", "r") as input_file:\n    text = input_file.read()\n\nhtml = markdown.markdown(, extensions=["md_redact"])\n\n# html == \'<p>This is <span class="redacted">(redacted)</span> in a markdown document.</p>\'\n```\n\nOr from the command line:\n\n```shell\nMD_REDACT_CONTENT=1 python -m markdown -x md_redact filename.md\n```\n\n# Why?\nProcessing markdown for a project where some users were allowed to see specific\ncontent while others were not. Figured an inline processor might be easier than\nlocking the users lacking permissions out of the page entirely.\n',
    'author': 'Will Mooney',
    'author_email': 'will.mooney.3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/willmooney3/md-redact',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
