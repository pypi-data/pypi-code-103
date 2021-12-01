# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['escriptorium_connector', 'escriptorium_connector.dtos']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.6.4,<5.0.0', 'requests==2.23.0', 'websocket-client>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'escriptorium-connector',
    'version': '0.0.21',
    'description': 'This simple python package makes it easy to connect to an eScriptorium instance and to work with the data there.',
    'long_description': "[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]\n\n# Escriptorium Connector\n\nThis simple python package makes it easy to connect to escriptorium and work with the data stored there.\n\n## Installation\n\nAnd the obligatory: `pip install escriptorium-connector`\n## Usage\n\nIf you are working on a public repository, you will probably want to store your user credentials in a hidden `.env` file that does not get distributed with your code. This is pretty easy to accomplish with [python-dotenv](https://pypi.org/project/python-dotenv/). You will need to provide the connector with an eScriptorium instance URL, the API your username, and your password (see below).\n\nThe `EscriptoriumConnector` class provides (or will provide) all the methods needed to interact programmatically with the eScriptorium platform.\n\nExample usage:\n\n```python\nfrom escriptorium_connector import EscriptoriumConnector\nimport os\nfrom dotenv import load_dotenv\n\n\nif __name__ == '__main__':\n    load_dotenv()\n    url = str(os.getenv('ESCRIPTORIUM_URL'))\n    username = str(os.getenv('ESCRIPTORIUM_USERNAME'))\n    password = str(os.getenv('ESCRIPTORIUM_PASSWORD'))\n    escr = EscriptoriumConnector(url, username, password)\n    print(escr.get_documents())\n\n```\n\nAnd your `.env` file should have:\n\n```txt\nESCRIPTORIUM_URL=https://www.escriptorium.fr\nESCRIPTORIUM_USERNAME=your_escriptorium_username\nESCRIPTORIUM_PASSWORD=your_escriptorium_password\n```\n\nSee [this Jupyter notebook](https://gitlab.com/sofer_mahir/escriptorium_python_connector/-/blob/main/example.ipynb) for a longer introduction to the connector.\n\n# Development\n\nWant to contribute? There is a lot to be done here, so we are happy for any PRs and updates.\n\n## Development Environment\n\nThis project uses Poetry. To start development, please pull down the repo from GitLab and run `poetry install`, which will make sure you have all the needed dependencies for the project and that you are using a valid Python version. Please use `poetry add <your-pip-package>` to install any new dependencies to the project so that they will be tracked by poetry.\n\n## Uploading to Pypi\n\nPoetry also makes uploading to Pypi very easy. Just confirm that all the package details in `pyproject.toml` are correct, bump the version of the package `poetry version 0.0.15`, and then use `poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD`, assuming you have set the environment variables `$PYPI_USERNAME` and `$PYPI_PASSWORD` appropriately (if you are using a Pypi token, then `PYPI_USERNAME=__token__` and `$PYPI_PASSWORD=<your-full-pypi-token>`).",
    'author': 'Bronson Brown-deVost',
    'author_email': 'bronsonbdevost@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/sofer_mahir/escriptorium_python_connector',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
