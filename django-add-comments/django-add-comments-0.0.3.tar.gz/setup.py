# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['comments', 'comments.migrations', 'comments.templatetags']

package_data = \
{'': ['*'],
 'comments': ['docs/*',
              'static/css/*',
              'static/img/favicons/*',
              'templates/*',
              'templates/base_template/*',
              'templates/comment/*']}

install_requires = \
['Django>=3.2,<4.0',
 'django-crispy-forms>=1.13.0,<2.0.0',
 'django-extensions>=3.1.5,<4.0.0']

setup_kwargs = {
    'name': 'django-add-comments',
    'version': '0.0.3',
    'description': 'Add and display htmx comments to arbitrary Django models.',
    'long_description': '# Comments\n\nEnable basic commenting functionality for an arbitrary Django model that contains an `AbstractCommentable` mixin class.\n\n## Overview\n\n```python\nfrom comments.models import AbstractCommentable\n\n# sentinels/models.py\nclass Sentinel(AbstractCommentable): # arbitrary\n    title = models.CharField(max_length=50)\n    ...\n\n# comments/models.py\nclass AbstractCommentable(models.Model): # generic foreign relationships to comments\n    comments = GenericRelation(Comment, related_query_name="%(app_label)s_%(class)ss")\n\n    class Meta:\n        abstract = True\n```\n\nOnce setup, can dive into [understanding the frontend](./comments/docs/frontend.md) through the use of htmx and hyperscript.\n\n## Quickstart\n\n1. [Install app](./comments/docs/setup.md)\n2. [Add generic comments to your model](./comments/docs/add_comments.md)\n\n## Premises\n\nAny model e.g. `Essay`, `Article`, etc... and (not just `Sentinel`) can be "commentable". But for purposes of demonstration, we\'ll use "sentinel" to refer to the arbitrary model that will have its own `comments` field.\n\nMore specifically, the instances of such sentinel – e.g. Sentinel with _id=1_, Sentinel with _id=2_, etc. – need to have their own related comments. This means having the ability to:\n\n1. View a list of existing comments on sentinel _id=1_\n2. Adding a comment (if logged in) on sentinel _id=2_\n3. Deleting a comment (if made by an `author`)\n4. Updating an added comment\'s `content` (if made by an `author`)\n5. Toggling visibility of the comment to the public.\n\nAll instances of the `Sentinel` model therefore will need their own commenting actions.\n',
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/justmars/django-add-comments',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
