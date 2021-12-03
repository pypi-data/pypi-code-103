# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wagtail_tenants',
 'wagtail_tenants.customers',
 'wagtail_tenants.customers.migrations',
 'wagtail_tenants.management',
 'wagtail_tenants.management.commands',
 'wagtail_tenants.middleware',
 'wagtail_tenants.migrations',
 'wagtail_tenants.users',
 'wagtail_tenants.users.migrations',
 'wagtail_tenants.users.views']

package_data = \
{'': ['*'],
 'wagtail_tenants': ['templates/wagtail_tenants/admin/*',
                     'templates/wagtailadmin/home/*',
                     'templates/wagtailusers/users/*']}

install_requires = \
['django-tenants>=3.3.4,<4.0.0', 'wagtail>=2.15.1,<3.0.0']

extras_require = \
{'docs': ['sphinx>=3,<4']}

setup_kwargs = {
    'name': 'wagtail-tenants',
    'version': '0.1.2',
    'description': 'Adds multitenancy based on django_tenants to wagtail cms',
    'long_description': None,
    'author': 'Boris Brue',
    'author_email': 'boris@zuckersalzundpfeffer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
