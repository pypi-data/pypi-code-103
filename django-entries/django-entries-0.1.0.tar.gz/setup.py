# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_entries', 'django_entries.migrations', 'django_entries.tests']

package_data = \
{'': ['*'],
 'django_entries': ['static/css/*', 'static/img/favicons/*', 'templates/*']}

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
    'version': '0.1.0',
    'description': 'Entries is a Django app that has basic CRUD functionality with some defaults.',
    'long_description': '# Entries\n\nEntries is a Django app that has basic CRUD functionality with some defaults.\n\nDetailed documentation is in the "docs" directory.\n\n## Quick start\n\n1. Add "entries" to your INSTALLED_APPS setting like this::\n\n   INSTALLED_APPS = [\n   ...\n   \'entries\',\n   ]\n\n2. Include the entries URLconf in your project urls.py like this::\n\n   path(\'entries/\', include(\'entries.urls\')),\n\n3. Run `python manage.py migrate` to create the entries models.\n',
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
