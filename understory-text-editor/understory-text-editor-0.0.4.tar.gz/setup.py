# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory',
 'understory.apps.text_editor',
 'understory.apps.text_editor.templates']

package_data = \
{'': ['*']}

install_requires = \
['micropub>=0.0.4,<0.0.5', 'understory>=0,<1']

entry_points = \
{'web.apps': ['text_editor = understory.apps.text_editor:app']}

setup_kwargs = {
    'name': 'understory-text-editor',
    'version': '0.0.4',
    'description': 'A text editor for the Understory framework.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'self@angelogladding.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
