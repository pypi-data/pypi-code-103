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
['Django>=4.0,<5.0',
 'django-crispy-forms>=1.13.0,<2.0.0',
 'django-extensions>=3.1.5,<4.0.0']

setup_kwargs = {
    'name': 'django-add-comments',
    'version': '0.0.4',
    'description': 'Add and display htmx comments to arbitrary Django models.',
    'long_description': '# Comments\n\nEnable basic commenting for an arbitrary Django model.\n\n```python\n# app_model/models.py\nfrom comment.models import AbstractCommentable\nclass Sentinel(AbstractCommentable):\n    """Any `app_model` e.g. `Essay`, `Article`, etc... can be "commentable". We\'ll use `Sentinel`, as a demo, to refer to an arbitrary model that will have its own `comments` field mapped to a generic `Comment` model because of inheriting from the `AbstractCommentable` mixin."""\n    title = models.CharField(max_length=50)\n```\n\nThe instances – e.g. `Sentinel` with _id=1_, `Sentinel` with _id=2_, etc. – will have their own related `Comment`s. `django-add-comments` also includes ability to:\n\n1. View a list of existing comments on sentinel _id=1_\n2. Adding a comment (if logged in) on sentinel _id=2_\n3. Deleting a comment (if made by the `author` of such comment)\n4. Updating an added comment\'s `content` (if made by an `author` of such comment)\n5. Toggling visibility of the comment to the public (if made by an `author` of such comment).\n\n## Quickstart\n\n1. [Install](./comments/docs/setup.md) django-add-comments app\n2. [Configure](./comments/docs/add_comments.md) target model\'s properties, urls, template\n3. Once setup, can dive into understanding htmx-driven [frontend](./comments/docs/frontend.md).\n4. The [procedure](./comments/docs/add_comments.md) described in the docs related to a hypothetical `Sentinel` model. For another Django app, let\'s say an `articles` app with an `Article` model, the same procedure can be followed.\n',
    'author': 'Marcelino G. Veloso III',
    'author_email': 'mars@veloso.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/justmars/django-add-comments',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
