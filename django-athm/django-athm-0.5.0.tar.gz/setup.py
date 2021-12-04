# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_athm',
 'django_athm.management',
 'django_athm.management.commands',
 'django_athm.migrations',
 'django_athm.templatetags']

package_data = \
{'': ['*'], 'django_athm': ['templates/*']}

install_requires = \
['httpx>=0.21.1,<0.22.0']

setup_kwargs = {
    'name': 'django-athm',
    'version': '0.5.0',
    'description': 'Django + ATH Móvil',
    'long_description': "# django-athm\n\n![Build Status](https://github.com/django-athm/django-athm/actions/workflows/ci.yaml/badge.svg)\n[![Codecov status](https://codecov.io/gh/django-athm/django-athm/branch/main/graph/badge.svg)](https://codecov.io/gh/django-athm/django-athm)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-athm)\n![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-athm)\n[![PyPI version](https://img.shields.io/pypi/v/django-athm.svg)](https://pypi.org/project/django-athm/)\n[![Packaged with Poetry](https://img.shields.io/badge/package_manager-poetry-blue.svg)](https://python-poetry.org/)\n![Code style badge](https://badgen.net/badge/code%20style/black/000)\n![License badge](https://img.shields.io/github/license/django-athm/django-athm.svg)\n\n_Ver este README en español: [README_ES.md](/README_ES.md)_\n\n## Features\n\n* Persist transactions and item references in your own database.\n* The customizable `athm_button` template tag provides convenient access to the ATH Móvil Checkout button.\n* Import your existing transactions from ATH Móvil using the `athm_sync` management command.\n* Various signals can be used to get notified of completed, cancelled or expired transactions.\n* Refund one or more transactions through the Django Admin.\n\n\n## Documentation\n\nFor information on installation and configuration, see the documentation at:\n\nhttps://django-athm.github.io/django-athm/\n\n## Local testing with coverage\n\nAssuming you've already installed all the packages, you can run the following command in the project root folder:\n\n```bash\nDJANGO_SETTINGS_MODULE=tests.settings pytest --cov django_athm\n```\n\n## Legal\n\nThis project is not affiliated with or endorsed by [Evertec, Inc.](https://www.evertecinc.com/) or [ATH Móvil](https://portal.athmovil.com/) in any way.\n\n\n## References\n\n- https://github.com/evertec/athmovil-javascript-api\n\n- https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax\n\n- https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/\n\n",
    'author': 'Raúl Negrón',
    'author_email': 'raul.esteban.negron@gmail.com',
    'maintainer': 'Raúl Negrón',
    'maintainer_email': 'raul.esteban.negron@gmail.com',
    'url': 'https://github.com/django-athm/django-athm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
