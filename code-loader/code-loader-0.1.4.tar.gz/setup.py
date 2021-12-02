# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['code_loader', 'code_loader.contract', 'code_loader.dataset_binder']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.20.14,<2.0.0',
 'dataclasses==0.8',
 'google-cloud-storage>=1.43.0,<2.0.0',
 'numpy==1.19.5',
 'pandas>=1.0,<2.0',
 'scikit-image>=0.17,<0.18',
 'scikit-learn>=0.24.2,<0.25.0',
 'tensorflow-datasets>=4.4.0,<5.0.0',
 'tensorflow==2.6.2',
 'texthero>=1.1.0,<2.0.0',
 'transformers>=4.12.5,<5.0.0']

setup_kwargs = {
    'name': 'code-loader',
    'version': '0.1.4',
    'description': '',
    'long_description': '# tensorleap code loader\nUsed to load user code to tensorleap \n',
    'author': 'dorhar',
    'author_email': 'doron.harnoy@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tensorleap/code-loader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<3.7',
}


setup(**setup_kwargs)
