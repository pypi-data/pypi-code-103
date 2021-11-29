# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['jupyter_cell_extractor']

package_data = \
{'': ['*'], 'jupyter_cell_extractor': ['data/*']}

install_requires = \
['Jinja2==3.0.2',
 'MarkupSafe==2.0.1',
 'Pygments==2.10.0',
 'attrs==21.2.0',
 'bleach==4.1.0',
 'check-requirements-txt>=1.0.2,<2.0.0',
 'defusedxml==0.7.1',
 'entrypoints==0.3',
 'ipython_genutils==0.2.0',
 'jsonschema==4.0.1',
 'jupyter-client==7.0.6',
 'jupyter-core==4.8.1',
 'jupyterlab-pygments==0.1.2',
 'mistune==0.8.4',
 'nbclient==0.5.4',
 'nbconvert==6.2.0',
 'nbformat==5.1.3',
 'nest-asyncio==1.5.1',
 'packaging==21.0',
 'pandocfilters==1.5.0',
 'pyparsing==2.4.7',
 'pyrsistent==0.18.0',
 'python-dateutil==2.8.2',
 'pyzmq==22.3.0',
 'six==1.16.0',
 'testpath==0.5.0',
 'tornado==6.1',
 'traitlets==5.1.0',
 'webencodings==0.5.1']

setup_kwargs = {
    'name': 'jupyter-cell-extractor',
    'version': '1.0.0',
    'description': '""',
    'long_description': None,
    'author': 'jaimebw',
    'author_email': 'jaimebwv@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
