# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['search_placeholder', 'search_placeholder.templatetags']

package_data = \
{'': ['*'],
 'search_placeholder': ['templates/admin/*', 'templates/search_placeholder/*']}

install_requires = \
['Django>=3.0,<4.0']

setup_kwargs = {
    'name': 'search-placeholder',
    'version': '0.1.1',
    'description': 'Auto add placeholder content for django admin',
    'long_description': '# django-search-placeholder\nAuto add placeholder content for django admin\n\n## Install\n- By git\n```bash\npip install git+https://hub.fastgit.org/waketzheng/django-search-placeholder.git\n```\n\n## Usage\n\n1. Add app name to settings\n```py\nINSTALLED_APPS = [\n    ...\n    "django.contrib.admin",\n    ...\n    "search_placeholder",\n    ...\n]\n```\n2. Use search_placeholder.ModelAdmin to replace admin.ModelAdmin\n```\nfrom django.contrib import admin\nfrom search_placeholder import ModelAdmin\n\n@admin.register(ModelClass)\nclass ModelClassAdmin(ModelAdmin):\n    # Just inherit from search_placeholder.ModelAdmin\n    # it will auto generate placeholder of search input by\n    # the verbose_name of \'field1\' and \'field2\'\n    # Or you can uncomment the next line to custom placeholder\n    #search_placeholder = \'Custom content\'\n    search_fields = (\'field1\', \'field2\')\n```\n',
    'author': 'Waket Zheng',
    'author_email': 'waketzheng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/waketzheng/django-search-placeholder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
