# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saagieapi', 'saagieapi.manager', 'saagieapi.projects']

package_data = \
{'': ['*']}

install_requires = \
['gql>=2.0.0,<3.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'saagieapi',
    'version': '0.5.6',
    'description': 'Python API to interact with Saagie',
    'long_description': '<p align="center"><img width=100% src="https://github.com/saagie/api-saagie/blob/master/.github/banner.png"></p>\n\n[![PyPI version](https://img.shields.io/pypi/v/saagieapi?style=for-the-badge)](https://pypi.org/project/saagieapi/)\n![PyPI version](https://img.shields.io/pypi/pyversions/saagieapi?style=for-the-badge)\n\n[![GitHub release date](https://img.shields.io/github/release-date/saagie/api-saagie?style=for-the-badge&color=blue)][releases]\n\n[![Contributors](https://img.shields.io/github/contributors/saagie/api-saagie?style=for-the-badge&color=black)][contributors]\n![License](https://img.shields.io/pypi/l/saagieapi?style=for-the-badge&color=black)\n\n[releases]: https://github.com/saagie/api-saagie/releases\n[contributors]: https://github.com/saagie/api-saagie/graphs/contributors\n\n- [Presentation](#presentation)\n- [Installation](#installation)\n- [Usage](#usage)\n  * [Projects](#projects)\n- [Contributing](#contributing)\n\n## Presentation\nThe `saagieapi` python package implements python API wrappers to easily interact with the Saagie platform in python.\n\nThere are two subpackages that each give access to a main class whose methods allows to interact with the API :\n* The `manager` subpackage implements the `SaagieApiManager` class whose methods can interact with the `manager` interface in Saagie (Saagie legacy)\n* The `projects` subpackage implements the `SaagieApi` class whose methods can interact with the `Projects` interface in Saagie (current main interface)\n\n## Installing\n\n```bash\npip install saagieapi==<version>\n```\n\n## Usage\n\n### Projects\n\n```python\nfrom saagieapi.projects import SaagieApi\n\nsaagie = SaagieApi(url_saagie="<url>",\n                   id_platform="1",\n                   user="<saagie-user-name>",\n                   password="<saagie-user-password>",\n                   realm="saagie")\n\n# Create a project named \'Project_test\' on the saagie platform\nproject_dict = saagie.create_project(name="Project_test",\n                                     group="<saagie-group-with-proper-permissions>",\n                                     role=\'Manager\',\n                                     description=\'A test project\')\n\n# Save the project id\nproject_id = project_dict[\'createProject\'][\'id\']\n\n# Create a python job named \'Python test job\' inside this project\njob_dict = saagie.create_job(job_name="Python test job",\n                             project_id=project_id,\n                             file=\'<path-to-local-file>\',\n                             description=\'Amazing python job\',\n                             category=\'Processing\',\n                             technology=\'python\',\n                             runtime_version=\'3.6\',\n                             command_line=\'python {file} arg1 arg2\',\n                             release_note=\'\',\n                             extra_technology=\'\'\n                             )\n\n# Save the job id\njob_id = job_dict[\'data\'][\'createJob\'][\'id\']\n\n# Run the python job and wait for its completion\nsaagie.run_job_callback(job_id=job_id, freq=10, timeout=-1)\n\n```\n\n## Contributing\n\nAll contributions are made with the pull-request system.\nPlease follow the following steps:\n\n- Create an issue with the correct label (i.e. Documentation/Bug/Feature)\n- Create a new branch starting with the issue type : `feat/...`, `fix/...` or `doc/...`. GitHub Action (CI) will be triggered on each push on your branch. Warning, after the first push on your branch, an automatic commit/push will be made by the CI in order to increment the version. Thus, remember to update your repository after your first commit.\n- Implement your change\n- Open a Pull Request (don\'t forget to link the PR to the issue)\n- PR will be reviewed by the Professional Service Team and merged if all the checks are successful\n\n### Commits Guidelines\n\nWe\'re using the [Python Semantic Release library](https://python-semantic-release.readthedocs.io/en/latest/) to manage our versioning. \n\nIn order to work properly, you need to follow the  [Emoji Parser commit style](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#major-emoji) when squashing the commits during the merge of the PR to master.  \n- Messages with :ambulance:, :lock:, :bug:, :zap:, :goal_net:, :alien:, :wheelchair:, :speech_balloon:, :mag:, :apple:, :penguin:, :checkered_flag:, :robot:, :green_apple: emojis in the commit will make the release process to bump the patch version\n- Messages with :sparkles:, :children_crossing:, :lipstick:, :iphone:, :egg:, :chart_with_upwards_trend: emojis in the commit will make the release process to bump the minor version\n- Messages with a :boom: emoji in the commit will make the release process to bump the major version\n',
    'author': 'Saagie',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/saagie/api-saagie',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
