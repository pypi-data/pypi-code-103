# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['darksearch']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0',
 'rich>=10.15.1,<11.0.0',
 'types-requests>=2.26.1,<3.0.0']

entry_points = \
{'console_scripts': ['darksearch = darksearch.cli:main']}

setup_kwargs = {
    'name': 'darksearch',
    'version': '2.1.3',
    'description': 'Python API wrapper for DarkSearch (darksearch.io).',
    'long_description': '# DarkSearch\n\n[![PyPI](https://img.shields.io/pypi/v/darksearch?color=orange&logo=pypi&logoColor=orange)](https://pypi.org/project/darksearch/)\n[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue?logo=python)](https://www.python.org/downloads/)\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/thehappydinoa/DarkSearch/test?label=tests)](https://github.com/thehappydinoa/DarkSearch/actions)\n[![Read the Docs](https://img.shields.io/readthedocs/darksearch/latest)](https://censys-python.readthedocs.io/en/stable/?badge=stable)\n[![License](https://img.shields.io/github/license/thehappydinoa/DarkSearch)](LICENSE)\n\nPython API wrapper for DarkSearch ([darksearch.io](https://darksearch.io/)). Python 3.6+ is currently supported.\n\n## Install\n\n```bash\npip install darksearch\n```\n\n## Resources\n\n- [Documentation](https://darksearch.readthedocs.io/)\n\n## Contributing\n\nAll contributions (no matter how small) are always welcome.\n\n## Development\n\n```bash\ngit clone git@github.com:thehappydinoa/DarkSearch.git\npoetry install\n```\n\n## Testing\n\n```bash\npytest\n```\n\n## Publishing\n\n```bash\npoetry build\npoetry publish\n```\n\n## License\n\nThis software is licensed under [MIT](LICENSE)\n',
    'author': 'Aidan Holland',
    'author_email': 'thehappydinoa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thehappydinoa/DarkSearch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
