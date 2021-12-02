# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_praetorian']

package_data = \
{'': ['*'], 'flask_praetorian': ['templates/*']}

install_requires = \
['flask-buzz>=0.1.7',
 'flask-mail>=0.9.1,<0.10.0',
 'flask>=1.0,<3.0',
 'passlib>=1.7,<2.0',
 'pendulum>=2.1,<3.0',
 'pyjwt>=2.0,<3.0']

setup_kwargs = {
    'name': 'flask-praetorian',
    'version': '1.3.0',
    'description': 'Strong, Simple, and Precise security for Flask APIs (using jwt)',
    'long_description': ".. image::  https://badge.fury.io/py/flask-praetorian.svg\n   :target: https://badge.fury.io/py/flask-praetorian\n   :alt:    Latest Published Version\n\n.. image::  https://travis-ci.org/dusktreader/flask-praetorian.svg?branch=master\n   :target: https://travis-ci.org/dusktreader/flask-praetorian\n   :alt:    Build Status\n\n.. image::  https://readthedocs.org/projects/flask-praetorian/badge/?version=latest\n   :target: http://flask-praetorian.readthedocs.io/en/latest/?badge=latest\n   :alt:    Documentation Build Status\n\n******************\n flask-praetorian\n******************\n\n---------------------------------------------------\nStrong, Simple, and Precise security for Flask APIs\n---------------------------------------------------\n\nAPI security should be strong, simple, and precise like a Roman Legionary.\nThis package aims to provide that. Using `JWT <https://jwt.io/>`_ tokens as\nimplemented by `PyJWT <https://pyjwt.readthedocs.io/en/latest/>`_,\n*flask_praetorian* uses a very simple interface to make sure that the users\naccessing your API's endpoints are provisioned with the correct roles for\naccess.\n\nThis project was heavily influenced by\n`Flask-Security <https://pythonhosted.org/Flask-Security/>`_, but intends\nto supply only essential functionality. Instead of trying to anticipate the\nneeds of all users, *flask-praetorian* will provide a simple and secure mechanism\nto provide security for APIs specifically.\n\nThis extesion offers a batteries-included approach to security for your API.\nFor essential security concerns for Flask-based APIs,\n`flask-praetorian <https://github.com/dusktreader/flask-praetorian>`_ should\nsupply everything you need.\n\nThe *flask-praetorian* package can be used to:\n\n* Hash passwords for storing in your database\n* Verify plaintext passwords against the hashed, stored versions\n* Generate authorization tokens upon verification of passwords\n* Check requests to secured endpoints for authorized tokens\n* Supply expiration of tokens and mechanisms for refreshing them\n* Ensure that the users associated with tokens have necessary roles for access\n* Parse user information from request headers for use in client route handlers\n* Support inclusion of custom user claims in tokens\n* Register new users using email verification\n\nAll of this is provided in a very simple to configure and initialize flask\nextension. Though simple, the security provided by *flask-praetorian* is strong\ndue to the usage of the proven security technology of JWT\nand python's `PassLib <http://pythonhosted.org/passlib/>`_ package.\n\nSuper-quick Start\n-----------------\n - requirements: `python` versions 3.6+\n - install through pip: `$ pip install flask-praetorian`\n - minimal usage example: `example/basic.py <https://github.com/dusktreader/flask-praetorian/tree/master/example/basic.py>`_\n\nDocumentation\n-------------\n\nThe complete documentation can be found at the\n`flask-praetorian home page <http://flask-praetorian.readthedocs.io>`_\n",
    'author': 'Tucker Beck',
    'author_email': 'tucker.beck@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://flask-praetorian.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
