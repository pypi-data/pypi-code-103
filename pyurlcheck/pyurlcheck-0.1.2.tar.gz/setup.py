# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyurlcheck']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'dnspython>=2.1.0,<3.0.0', 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['pyurlcheck = pyurlcheck.cli:main']}

setup_kwargs = {
    'name': 'pyurlcheck',
    'version': '0.1.2',
    'description': 'Search docs and validate URLs found are working properly.',
    'long_description': "# PYURLCHECK\n\nProject is currently a **WIP**.\n\n`pyurlcheck` can be used to scan through all of a projects documents and validate any `public` facing URLs are still reachable.\n\n### Why??\nIt's apparent when navigating code documentation online that keeping up with URLs in documentation isn't always done properly.  Running into constant `404 Not Found` errors is frustrating for users that are trying to learn how to use a product or tool.\n\n### Examples\nRunning the tool against a single file.\n```python\n▶ python cli.py examples/example1.md                          \nexamples/example1.md:8  URL Issue: https://www.ansible.com/jeff\n```\n\nRunning the tool against a directory.  All files in the directory will be executed.\n```python\n▶ python cli.py examples/           \nexamples/example2.md:6  URL Issue: https://www.ansible.com/jeff\nexamples/example1.md:8  URL Issue: https://www.ansible.com/fake\n```\n\nAlternatively,\n\nyou can replace `python cli.py` with `pyurlcheck` on the command line.\n\n```\n▶ pyurlcheck pyurlcheck/examples/\npyurlcheck/examples/example3.txt:4      URL Issue: https://www.ansible.com/jeff\npyurlcheck/examples/example2.md:7       URL Issue: https://www.ansible.com/jeff\npyurlcheck/examples/example3.md:3       URL Issue: https://www.ansible.com/jeff\npyurlcheck/examples/example4.rst:22     URL Issue: http://google.com/france\npyurlcheck/examples/example4.rst:23     URL Issue: http://google.com/japan\npyurlcheck/examples/example1.md:9       URL Issue: https://www.ansible.com/jeff\n```\n\nFile extensions are currently not checked; therefore all files in a directory that is passed in will be validated.\n\n## Installation\n\n```\npip install pyurlcheck\n```\n",
    'author': 'Jeff Kala',
    'author_email': 'jeff.l.kala@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jeffkala/pyurlcheck.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
