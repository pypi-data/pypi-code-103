# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quilt3_local', 'quilt3_local.lambdas', 'quilt3_local.lambdas.shared']

package_data = \
{'': ['*'], 'quilt3_local': ['catalog_bundle/*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'aicsimageio==3.0.7',
 'aiohttp>=3.8.1,<4.0.0',
 'ariadne>=0.14.0,<0.15.0',
 'boto3>=1.10.0,<2.0.0',
 'botocore>=1.23.14,<2.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'fastapi>=0.70.0,<0.71.0',
 'fcsparser>=0.2.4,<0.3.0',
 'imageio==2.5.0',
 'importlib-resources>=5.3.0,<6.0.0',
 'jsonschema>=3.0.1,<4.0.0',
 'nbconvert>=6.3.0,<7.0.0',
 'nbformat>=5.1.3,<6.0.0',
 'numpy>=1.21.4,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'requests>=2.26.0,<3.0.0',
 'uvicorn[standard]>=0.15.0,<0.16.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'quilt3-local',
    'version': '1.0.0b11',
    'description': '',
    'long_description': None,
    'author': 'Alexei Mochalov',
    'author_email': 'alexei@quiltdata.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
