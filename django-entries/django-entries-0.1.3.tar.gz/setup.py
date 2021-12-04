# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['entries', 'entries.migrations', 'entries.tests']

package_data = \
{'': ['*'], 'entries': ['static/css/*', 'templates/*']}

install_requires = \
['Django>=3.2,<4.0',
 'Markdown>=3.3.6,<4.0.0',
 'bleach>=4.1.0,<5.0.0',
 'django-crispy-forms>=1.13.0,<2.0.0',
 'django-extensions==3.1.5',
 'markdownify>=0.10.0,<0.11.0',
 'types-Markdown>=3.3.8,<4.0.0',
 'types-bleach>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'django-entries',
    'version': '0.1.3',
    'description': 'Entries is a Django app that has basic CRUD functionality with some defaults.',
    'long_description': '# Entries\n\nEntries is a Django app that has basic CRUD functionality with some defaults.\n\n## What is included?\n\nThe `templates/base.html` includes:\n\n1. `starter.css` [stylesheet](entries/static/css/starter.css) for some defaults\n2. `pylon` 0.1.1 for `<hstack>` and `<vstack>` layouts\n3. `htmx` 1.6.1 for html-over-the-wire functionality\n4. `hyperscript` 0.9 for client-side reactivity\n5. `simplemde` a simple text editor that accepts markdown\n\n## Quick start\n\n### 1: Add to apps\n\nAdd "entries" to your INSTALLED_APPS setting like this:\n\n```python\nINSTALLED_APPS = [\n...\n\'crispy_forms\'\n\'entries\',\n]\n```\n\n### 2: Add to urls\n\nInclude the entries URLconf in your project urls.py like this:\n\n```python\nurlpatterns = [\n...\npath(\'\', include(\'entries.urls\')),\n]\n```\n\n### 3: Add to db\n\nRun `python manage.py migrate` to create the entries models.\n',
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
