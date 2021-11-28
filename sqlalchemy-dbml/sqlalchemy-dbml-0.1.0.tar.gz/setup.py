# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlalchemy_dbml']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.27,<2.0.0',
 'rich>=10.15.0,<11.0.0',
 'sqlmodel>=0.0.4,<0.0.5',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['dbml = sqlalchemy_dbml.main:app']}

setup_kwargs = {
    'name': 'sqlalchemy-dbml',
    'version': '0.1.0',
    'description': 'Convert SQLAlchemy/SQLModel into DBML, and the other way around! 🎉',
    'long_description': '<h1 align="center">\n    <strong>sqlalchemy-dbml</strong>\n</h1>\n<p align="center">\n    <a href="https://github.com/Kludex/sqlalchemy-dbml" target="_blank">\n        <img src="https://img.shields.io/github/last-commit/Kludex/sqlalchemy-dbml" alt="Latest Commit">\n    </a>\n        <img src="https://img.shields.io/github/workflow/status/Kludex/sqlalchemy-dbml/Test">\n        <img src="https://img.shields.io/codecov/c/github/Kludex/sqlalchemy-dbml">\n    <br />\n    <a href="https://pypi.org/project/sqlalchemy-dbml" target="_blank">\n        <img src="https://img.shields.io/pypi/v/sqlalchemy-dbml" alt="Package version">\n    </a>\n    <img src="https://img.shields.io/pypi/pyversions/sqlalchemy-dbml">\n    <img src="https://img.shields.io/github/license/Kludex/sqlalchemy-dbml">\n</p>\n\n\n## Installation\n\n``` bash\npip install sqlalchemy-dbml\n```\n\n## Usage\n\n```bash\ndbml <module>:<base_class>\n```\n\n## References\n\n- [DBML - Database Markup Language](https://www.dbml.org/home/#intro)\n- [DBML parser for Python](https://github.com/Vanderhoof/PyDBML)\n- [Django DBML generator](https://github.com/makecodes/django-dbml/tree/master)\n- [DbmlForDjango](https://github.com/hamedsj/DbmlForDjango)\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    'author': 'Marcelo Trylesinski',
    'author_email': 'marcelotryle@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kludex/sqlalchemy-dbml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
