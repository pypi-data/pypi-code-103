# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['xdf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'xdf',
    'version': '0.0.0.dev0',
    'description': 'Data Frames / Data Feeders with high-level abstractions for key tasks in AI applications',
    'long_description': '# Data Frames / Data Feeders with high-level abstractions for key tasks in AI applications\n',
    'author': 'STEAM for Vietnam Foundation AI & Robotics Educational Initiative',
    'author_email': 'Edu.AI@STEAMforVietNam.org',
    'maintainer': 'STEAM for Vietnam Foundation AI & Robotics Educational Initiative',
    'maintainer_email': 'Edu.AI@STEAMforVietNam.org',
    'url': 'https://GitHub.com/Django-AI/XDF',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
