# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bavard_ml_utils',
 'bavard_ml_utils.gcp',
 'bavard_ml_utils.ml',
 'bavard_ml_utils.persistence',
 'bavard_ml_utils.persistence.record_store',
 'bavard_ml_utils.types',
 'bavard_ml_utils.types.conversations',
 'bavard_ml_utils.web']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.63.0,<1.0.0',
 'loguru>=0.5.1,<1.0.0',
 'pydantic>=1.7.3,<2.0.0',
 'requests>=2.21.0,<3.0.0']

extras_require = \
{'aws': ['boto3>=1.20.16,<2.0.0'],
 'gcp': ['google-cloud-storage>=1.35.1,<2.0.0',
         'google-cloud-pubsub>=2.2.0,<3.0.0',
         'google-cloud-error-reporting>=1.1.1,<2.0.0',
         'google-cloud-firestore>=2.3.2,<3.0.0'],
 'ml': ['numpy>=1.19.2,<2.0.0',
        'scikit-learn>=0.24.2,<2.0.0',
        'networkx>=2.6.3,<3.0.0']}

setup_kwargs = {
    'name': 'bavard-ml-utils',
    'version': '0.2.9',
    'description': 'Utilities for machine learning, python web services, and cloud infrastructure',
    'long_description': '# bavard-ml-utils\n\n[![CircleCI Build Status](https://circleci.com/gh/bavard-ai/bavard-ml-utils/tree/main.svg?style=shield)](https://circleci.com/gh/bavard-ai/bavard-ml-utils/tree/main)\n[![PyPI Version](https://badge.fury.io/py/bavard-ml-utils.svg)](https://badge.fury.io/py/bavard-ml-utils)\n[![PyPI Downloads](https://pepy.tech/badge/bavard-ml-utils)](https://pepy.tech/project/bavard-ml-utils)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bavard-ml-utils)](https://pypi.org/project/bavard-ml-utils/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\nA package of common code and utilities for machine learning and MLOps. Includes classes and methods for:\n\n1. ML model serialization/deserialization\n2. Google Cloud Storage IO operations\n3. Converting a ML model into a runnable web service\n4. Common ML model evaluation utilities\n5. Common data structures/models used across the Bavard AI organization\n6. ML model artifact persistence and version management\n7. And more\n\nThis package maintains common data structures used across our organization. They can all be found in the `bavard_ml_utils.types` sub-package, and are all [Pydantic](https://pydantic-docs.helpmanual.io/) data models. For example the `bavard_ml_utils.types.agent.AgentConfig` class represents a chatbot\'s configuration and training data, and is used heavily across Bavard.\n\nAPI docs for this package can be found [here](https://docs-bavard-ml-utils.web.app/).\n\n## Getting Started\n\nTo begin using the package, use your favorite package manager to install it from PyPi. For example, using pip:\n\n```\npip install bavard-ml-utils\n```\n\nSome of the features in this repo require more heavy weight dependencies, like Google Cloud Platform related utilities, or utilities specific to machine-learning. If you try to import those features, they will tell you if you do not have the correct package extra installed. For example, many of the features in the `bavard_ml_utils.gcp` sub-package require the `gcp` extra. To install `bavard-ml-utils` with that extra:\n\n```\npip install bavard-ml-utils[gcp]\n```\n\nYou can then begin using any package features that require GCP dependencies.\n\n## Developing Locally\n\nBefore making any new commits or pull requests, please complete these steps.\n\n1. Install the Poetry package manager for Python if you do not already have it. Installation instructions can be found [here](https://python-poetry.org/docs/#installation).\n2. Clone the project:\n   ```\n   git clone https://github.com/bavard-ai/bavard-ml-utils.git\n   cd bavard-ml-utils\n   ```\n3. Install the dependencies, including all dev dependencies and extras:\n   ```\n   poetry install --extras "gcp ml"\n   ```\n4. Install the pre-commit hooks, so they will run before each local commit. This includes linting, auto-formatting, and import sorting:\n   ```\n   pre-commit install\n   ```\n\n## Testing Locally\n\nWith Docker and docker-compose installed, run this script from the project root:\n\n```\n./scripts/lint-and-test-package.sh\n```\n\n## Releasing The Package\n\nReleasing the package is automatically handled by CI, but three steps must be taken to trigger a successful release:\n\n1. Use Poetry\'s [`version` command](https://python-poetry.org/docs/cli/#version) to bump the package\'s version.\n2. Commit and tag the repo with the exact same version the package was bumped to, e.g. `1.0.0` (note there is no preceding `v`.)\n3. Push the commit and tag to remote. These can be done together using: `git push --atomic origin <branch name> <tag>`\n\nCI will then build release the package to pypi with that version once the commit and tag are pushed.\n',
    'author': 'Bavard AI, Inc.',
    'author_email': 'dev@bavard.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bavard-ai/bavard-ml-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
