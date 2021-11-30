# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['preprocess_cancellation']
extras_require = \
{'shapely': ['shapely']}

entry_points = \
{'console_scripts': ['preprocess_cancellation = preprocess_cancellation:_main']}

setup_kwargs = {
    'name': 'preprocess-cancellation',
    'version': '0.1.5.post1',
    'description': 'GCode processor to add klipper cancel-object markers',
    'long_description': None,
    'author': 'Franklyn Tackitt',
    'author_email': 'im@frank.af',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kageurufu/cancelobject-preprocessor',
    'py_modules': modules,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.0',
}


setup(**setup_kwargs)
