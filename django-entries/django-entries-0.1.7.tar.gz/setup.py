# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['entries', 'entries.migrations', 'entries.tests']

package_data = \
{'': ['*'], 'entries': ['static/css/*', 'static/img/favicons/*', 'templates/*']}

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
    'version': '0.1.7',
    'description': 'Entries is a helper Django app with CRUD functions based on htmx.',
    'long_description': "# Entries\n\n## Overview\n\nEntries is a Django app that has basic create-read-update-delete functionality for a model that `Entry` consisting of the following fields: `title`, `excerpt`,`content` and `author`.\n\nThe [templates/base.html](./entries/templates/base.html) provides a light set of tools:\n\n1. `starter.css` [stylesheet](./entries/static/css/starter.css) for some defaults\n2. `pylon` 0.1.1 for `<hstack>` and `<vstack>` layouts\n3. `htmx` 1.6.1 for html-over-the-wire functionality\n4. `hyperscript` 0.9 for client-side reactivity\n5. `simplemde` a simple text editor that accepts markdown\n\n## Quickstart\n\n```python\n# in project_folder/settings.py\nINSTALLED_APPS = [\n    ...,\n    'crispy_forms',  # crispy_forms at least > v1.13\n    'entries' # new\n]\n\n# in project_folder/urls.py\nfrom django.urls import path, include # new\nurlpatterns = [\n    ...,\n    path('entry/', include('entries.urls')) # new\n]\n```\n\nAdd to database:\n\n```zsh\n.venv> python manage.py migrate # enter virtual environment\n```\n",
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/justmars/django-entries',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
