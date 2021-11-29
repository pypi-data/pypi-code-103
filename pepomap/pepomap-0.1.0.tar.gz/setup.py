# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pepomap']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.0,<4.0.0', 'numpy>=1.21.4,<2.0.0']

setup_kwargs = {
    'name': 'pepomap',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Pepomap\n\nJust some extra Matplotlib colormaps.\n\n## Installation\n\n```bash\npip install pepomap\n```\n\n## Colormaps\n\n```python\nimport pepomap\n\npepomap.tools.display_colormaps(pepomap.cmaps)\n```\n\n![pepomap_colormaps_darkbg](https://user-images.githubusercontent.com/12076399/143933964-18e03db4-890a-4756-b19f-9aba327532b5.png#gh-dark-mode-only)\n\n![pepomap_colormaps_lightbg](https://user-images.githubusercontent.com/12076399/143933201-f2a61bfa-2f34-4b3b-a5d2-c3a100061279.png#gh-light-mode-only)\n\n## How to use\n\n```python\nimport pepomap\n\ncmap = pepomap.cmaps["storm"]\n```\n',
    'author': 'ericmiguel',
    'author_email': 'ericmiguel@id.uff.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ericmiguel/pepomap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<3.11',
}


setup(**setup_kwargs)
