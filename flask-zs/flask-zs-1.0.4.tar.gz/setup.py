# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_zs', 'flask_zs.bin']

package_data = \
{'': ['*']}

install_requires = \
['Flask', 'SQLAlchemy', 'requests']

entry_points = \
{'console_scripts': ['collect-models = flask_zs.bin.collect_models:main']}

setup_kwargs = {
    'name': 'flask-zs',
    'version': '1.0.4',
    'description': 'A helpers for Flask.',
    'long_description': 'Helpers for Flask.\n====================\n\nHelpers for Flask. 使用示例 `codeif/flask-zs-template  <https://github.com/codeif/flask-zs-template>`_\n\n包含:\n\n- flask\n- sqlalchemy\n- requests\n\n\n安装\n----\n\n.. code-block:: sh\n\n    pip install flask-zs\n\n集中models\n-------------\n\n把models集中到models/__init__.py文件中(zsdemo为package name)::\n\n    PYTHONPATH=. collect-models [zsdemo]\n',
    'author': 'codeif',
    'author_email': 'me@codeif.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codeif/flask-zs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
