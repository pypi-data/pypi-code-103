# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['krippendorff']

package_data = \
{'': ['*']}

install_requires = \
['numpy']

setup_kwargs = {
    'name': 'krippendorff',
    'version': '0.5.1',
    'description': "Fast computation of the Krippendorff's alpha measure.",
    'long_description': "[![Actions Status](https://github.com/pln-fing-udelar/fast-krippendorff/workflows/CI/badge.svg)](https://github.com/pln-fing-udelar/fast-krippendorff/actions)\n[![Version](https://img.shields.io/pypi/v/krippendorff.svg)](https://pypi.python.org/pypi/krippendorff)\n[![License](https://img.shields.io/pypi/l/krippendorff.svg)](https://pypi.python.org/pypi/krippendorff)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/krippendorff.svg)](https://pypi.python.org/pypi/krippendorff)\n\n# Krippendorff\n\nFast computation of [Krippendorff's alpha](https://en.wikipedia.org/wiki/Krippendorff%27s_alpha) agreement measure.\n\nBased on [Thomas Grill implementation](https://github.com/grrrr/krippendorff-alpha).\n\n## Example usage\n\nGiven a reliability data matrix, run:\n\n```python\nimport krippendorff\n\nkrippendorff.alpha(reliability_data=...)\n```\n\nSee `sample.py` and `alpha`'s docstring for more details.\n\n## Installation\n\n```bash\npip install krippendorff\n```\n\n## Caveats\n\nThe implementation is fast as it doesn't do a nested loop for the coders. However, `V` should be small, since a `VxV` matrix it's used.\n",
    'author': 'Santiago Castro',
    'author_email': 'sacastro@fing.edu.uy',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pln-fing-udelar/fast-krippendorff',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
