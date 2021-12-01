# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dbxdeploy',
 'dbxdeploy.black',
 'dbxdeploy.cluster',
 'dbxdeploy.dbc',
 'dbxdeploy.dbfs',
 'dbxdeploy.deploy',
 'dbxdeploy.filesystem',
 'dbxdeploy.git',
 'dbxdeploy.job',
 'dbxdeploy.notebook',
 'dbxdeploy.notebook.converter',
 'dbxdeploy.package',
 'dbxdeploy.poetry',
 'dbxdeploy.repos',
 'dbxdeploy.shell',
 'dbxdeploy.string',
 'dbxdeploy.utils',
 'dbxdeploy.workspace']

package_data = \
{'': ['*'], 'dbxdeploy': ['_config/*']}

install_requires = \
['Jinja2>=2.0.0,<3.0.0',
 'console-bundle>=0.5,<0.6',
 'databricks-cli>=0.16.0,<0.17.0',
 'dbx-notebook-exporter>=0.4.0,<0.5.0',
 'nbconvert>=5.6.0,<6.0.0',
 'pyfony-bundles>=0.4.0,<0.5.0',
 'pyfony-core>=0.8.1,<0.9.0',
 'pygit2>=1.3,<2.0',
 'python-box>=3.4,<4.0',
 'tomlkit>=0.5.8,<1.0.0']

entry_points = \
{'pyfony.bundle': ['create = dbxdeploy.DbxDeployBundle:DbxDeployBundle']}

setup_kwargs = {
    'name': 'dbx-deploy',
    'version': '1.2.1a1',
    'description': 'Databricks Deployment Tool',
    'long_description': '# DBX deploy bundle\n\nThis bundle allows you to deploy notebooks along with custom code to Databricks. It is part of the [Daipe Framework](https://www.daipe.ai).  \n\n## Resources\n\n* [Documentation](https://docs.daipe.ai/deploy-demo-project/)\n',
    'author': 'Jiri Koutny',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/dbx-deploy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
