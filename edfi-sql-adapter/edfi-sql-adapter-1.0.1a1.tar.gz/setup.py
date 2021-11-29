# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edfi_sql_adapter']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy==1.3.23', 'psycopg2>=2.8.6,<3.0.0', 'pyodbc>=4.0.30,<5.0.0']

setup_kwargs = {
    'name': 'edfi-sql-adapter',
    'version': '1.0.1a1',
    'description': 'Lightweight wrapper to facilitate connections to SQL databases',
    'long_description': '# edfi-sql-adapter\n\nLightweight wrapper to facilitate connections to SQL databases.\n\n## Developer Notes\n\nThis package is light on unit tests, because the functions are well tested from\nan integration perspective. Would be nice to add unit tests for error handling\nin particular, but that would mean a lot of mocking of SQLAlchemy.\n\n## Legal Information\n\nCopyright (c) 2021 Ed-Fi Alliance, LLC and contributors.\n\nLicensed under the [Apache License, Version\n2.0](https://github.com/Ed-Fi-Exchange-OSS/LMS-Toolkit/blob/main/LICENSE) (the\n"License").\n\nUnless required by applicable law or agreed to in writing, software distributed\nunder the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR\nCONDITIONS OF ANY KIND, either express or implied. See the License for the\nspecific language governing permissions and limitations under the License.\n\nSee\n[NOTICES](https://github.com/Ed-Fi-Exchange-OSS/LMS-Toolkit/blob/main/NOTICES.md)\nfor additional copyright and license notifications.\n\n',
    'author': 'Ed-Fi Alliance, LLC, and contributors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://techdocs.ed-fi.org/display/EDFITOOLS/LMS+Toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
