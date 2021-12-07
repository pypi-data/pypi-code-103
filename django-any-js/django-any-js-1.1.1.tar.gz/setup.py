# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_any_js', 'django_any_js.templatetags']

package_data = \
{'': ['*'], 'django_any_js': ['templates/django_any_js/*']}

install_requires = \
['Django>=2.2,<5.0']

setup_kwargs = {
    'name': 'django-any-js',
    'version': '1.1.1',
    'description': 'Include JavaScript/CSS libraries with readable template tags',
    'long_description': 'Django Any-JS\n=============\n\nDescription\n-----------\n\nDjango-Any-JS helps you at including any combination of JavaScript/CSS\nURLs in your site, with readable settings and template tags.\n\nUsage\n-----\n\nIn your settings:\n\n::\n\n    INSTALLED_APPS = [\n        ...,\n        "django_any_js",\n        ...,\n    ]\n    ANY_JS = {\n        "DataTables": {\n            "js_url": "/javascript/jquery-datatables/dataTables.bootstrap4.min.js",\n            "css_url": "/javascript/jquery-datatables/css/dataTables.bootstrap4.min.css",\n        }\n    }\n\nIn your template:\n\n::\n\n    {% load any_js %}\n    {% include_js "DataTables" %}\n    {% include_css "DataTables" %}\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': 'Dominik George',
    'maintainer_email': 'dominik.george@teckids.org',
    'url': 'https://edugit.org/AlekSIS/libs/django-any-js',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
