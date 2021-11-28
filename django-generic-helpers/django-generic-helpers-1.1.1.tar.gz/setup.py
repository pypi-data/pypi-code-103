# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['generic_helpers']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-generic-helpers',
    'version': '1.1.1',
    'description': "A small toolset that helps you to work with Django's generic relations",
    'long_description': "======================\ndjango-generic-helpers\n======================\n\n.. image:: https://badge.fury.io/py/django-generic-helpers.svg\n   :target: http://badge.fury.io/py/django-generic-helpers\n\n\n.. image:: https://coveralls.io/repos/marazmiki/django-generic-helpers/badge.svg?branch=master\n   :target: https://coveralls.io/r/marazmiki/django-generic-helpers?branch=master\n\n.. image:: https://pypip.in/d/django-generic-helpers/badge.png\n   :target: https://pypi.python.org/pypi/django-generic-helpers\n\n.. image:: https://pypip.in/wheel/django-generic-helpers/badge.svg\n   :target: https://pypi.python.org/pypi/django-generic-helpers/\n   :alt: Wheel Status\n\n.. image:: https://img.shields.io/pypi/pyversions/django-generic-helpers.svg\n   :target: https://pypi.python.org/pypi/django-generic-helpers/\n   :alt: Supported Python versions\n\n.. image:: https://img.shields.io/pypi/djversions/django-generic-helpers.svg\n   :target: https://pypi.python.org/pypi/django-generic-helpers/\n   :alt: Supported Django versions\n\n\nThe application provides some syntax sugar for working with Django's `generic relations <https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/#generic-relations>`_\n\n\n\nInstallation\n============\n\nJust install the package from PyPI within ``pip``\n\n.. code:: bash\n\n    pip install django-generic-helpers\n\n...or `pipenv <https://docs.pipenv.org/en/latest/>`_\n\n.. code:: bash\n\n    pipenv install django-generic-helpers\n\n...or even `poetry <https://poetry.eustace.io/>`_\n\n.. code:: bash\n\n    poetry add django-generic-helpers\n\nThat's all. No need to add this into ``INSTALLED_APPS`` of your project or something like that.\n\n\nUsage\n=====\n\nThat's how did you work with generic relations before:\n\n.. code:: python\n\n    # models.py\n    from django.contrib.contenttypes.fields import GenericForeignKey\n    from django.contrib.contenttypes.models import ContentType\n    from django.db import models\n\n    class Post(models.Model):\n        pass\n\n    class Image(models.Model):\n         content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)\n         object_id = models.IntegerField()\n         content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')\n\n    # Example of filtering\n    post = Post.objects.get(pk=1)\n    images = Image.objects.filter(\n        content_type=ContentType.objects.get_for_object(post),\n        object_id=post.id\n    )\n\nLooks verbose a bit, yep? Let's rewrite this with ``django-generic-helpers``\n\n.. code:: python\n\n    # models.py\n    from django.db import models\n    from generic_helpers.fields import GenericRelationField\n\n    class Post(models.Model):\n        pass\n\n    class Image(models.Model):\n         content_object = GenericRelationField()\n\n    # Example of filtering\n    post = Post.objects.get(pk=1)\n    images = Image.objects.filter(content_object=post)\n\nPersonally, I found it much simpler and cleaner.\n\nFeatures the application provides:\n\n* Creating an arbitrary number of generic relation fields, both required and optional;\n* Providing custom names for ``content_type`` and ``object_id`` columns\n* You can define a whitelist (or a black one) of models that could (not) be written into the field\n\nPlease, follow up the documentation for details.\n\nContributing\n============\n\n* If you found a bug, feel free to drop me `an issue on the repo <https://github.com/marazmiki/django-generic-helpers/issues/new>`_;\n* Implemented a new feature could be useful? `Create a PR <https://github.com/marazmiki/django-generic-helpers/compare>`_!\n\nA few words if you plan to send a PR:\n\n* Please, write tests!\n* Follow `PEP-0008 <https://www.python.org/dev/peps/pep-0008/>`_ codestyle recommendations.\n* When pushing, please wait while `Travis CI <https://travis-ci.org/marazmiki/django-generic-helpers>`_ will finish his useful work and complete the build. And if the build fails, please fix the issues before PR\n* And of course, don't forget to add yourself into the `authors list <https://github.com/marazmiki/django-generic-helpers/blob/master/docs/authors.rst>`_ ;)\n\nLicense\n=======\n\nThe license is MIT.\n",
    'author': 'Mikhail Porokhovnichenko',
    'author_email': 'marazmiki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marazmiki/django-generic-helpers',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
