# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['guest_user',
 'guest_user.contrib.allauth',
 'guest_user.management',
 'guest_user.management.commands',
 'guest_user.migrations',
 'guest_user.templatetags']

package_data = \
{'': ['*'], 'guest_user': ['templates/guest_user/*']}

setup_kwargs = {
    'name': 'django-guest-user',
    'version': '0.4.0',
    'description': 'A Django app that lets visitors interact with your site without registration.',
    'long_description': '[![Code Lint](https://github.com/julianwachholz/django-guest-user/actions/workflows/lint.yml/badge.svg)](https://github.com/julianwachholz/django-guest-user/actions/workflows/lint.yml)\n[![Python Tests](https://github.com/julianwachholz/django-guest-user/actions/workflows/test.yml/badge.svg)](https://github.com/julianwachholz/django-guest-user/actions/workflows/test.yml)\n[![Documentation](https://readthedocs.org/projects/django-guest-user/badge/?style=flat)](https://django-guest-user.readthedocs.io)\n\n# django-guest-user\n\nA Django app that allows visitors to interact with your site as a guest user\nwithout requiring registration.\n\nLargely inspired by [django-lazysignup](https://github.com/danfairs/django-lazysignup) and rewritten for Django 3.1+ and Python 3.7+.\n\nFind the [**complete documentation**](https://django-guest-user.readthedocs.io/)\non Read the Docs.\n\n## Quickstart\n\n1. Install the `django-guest-user` package\n2. Add `guest_user` to your `INSTALLED_APPS` and migrate your database\n3. Add `guest_user.backends.GuestBackend` to your `AUTHENTICATION_BACKENDS`\n4. Include `guest_user.urls` in your URLs\n5. Decorate your views with `@allow_guest_user`:\n\n   ```\n   from guest_user.decorators import allow_guest_user\n\n   @allow_guest_user\n   def my_view(request):\n       assert request.user.is_authenticated\n       return render(request, "my_view.html")\n   ```\n\n## Status\n\nThis project is still under development. But thanks to [previous work](https://github.com/danfairs/django-lazysignup) it is largely functional.\n\nI decided to rewrite the project since the original project hasn\'t seen any\nlarger updates for a few years now. The initial code base was written a long\ntime ago as well.\n',
    'author': 'Julian Wachholz',
    'author_email': 'julian@wachholz.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/julianwachholz/django-guest-user',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
