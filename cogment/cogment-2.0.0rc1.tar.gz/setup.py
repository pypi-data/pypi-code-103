# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cogment', 'cogment.api']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-reflection>=1.30,<1.39',
 'grpcio>=1.30,<1.39',
 'prometheus-client>=0.8,<0.9',
 'protobuf>=3.7,<4.0']

extras_require = \
{'generate': ['PyYAML>=5.3.1,<6.0.0', 'grpcio-tools==1.38']}

setup_kwargs = {
    'name': 'cogment',
    'version': '2.0.0rc1',
    'description': 'Cogment python SDK',
    'long_description': '# cogment-py-sdk\n\n[![Latest final release](https://img.shields.io/pypi/v/cogment?style=flat-square)](https://pypi.org/project/cogment/) [![Apache 2 License](https://img.shields.io/badge/license-Apache%202-green?style=flat-square)](./LICENSE) [![Changelog](https://img.shields.io/badge/-Changelog%20-blueviolet?style=flat-square)](./CHANGELOG.md)\n\n[Cogment](https://cogment.ai) is an innovative open source AI platform designed to leverage the advent of AI to benefit humankind through human-AI collaboration developed by [AI Redefined](https://ai-r.com). Cogment enables AI researchers and engineers to build, train and operate AI agents in simulated or real environments shared with humans. For the full user documentation visit <https://docs.cogment.ai>\n\nThis module, `cogment-py-sdk`, is the Python SDK for making use of Cogment when working with Python. It\'s full documentation can be consulted at <https://docs.cogment.ai/cogment/cogment-api-reference/python/>.\n\n## Developers\n\n### Local setup\n\nMake sure you have the following installed:\n\n-   [Python](https://www.python.org) (any version >=3.7 should work),\n-   [Poetry](https://python-poetry.org).\n\nInstall the dependencies, including downloading and building the cogment protobuf API, by navigating to the python SDK directory and run the following\n\n```\npoetry install\n```\n\n### Define used Cogment protobuf API\n\nThe version of the used cogment protobuf API is defined in the `.cogment-api.yaml` file at the root of the repository. The following can be defined:\n\n-   `cogment_api_version: "latest"`, is the default, it retrieves the _latest_ build of the cogment-api `develop`,\n-   `cogment_api_version: "vMAJOR.MINOR.PATCH[-PRERELEASE]"`, retrieves an official release of cogment-api.\n-   `cogment_api_path: "../path/to/cogment-api"`, retrieves a local version of cogment-api found at the given path ; if set, this overrides `cogment_api_version`.\n\n> ⚠️ when building a docker image, `cogment_api_path` needs to exists in the docker file system. In practice it means it should be a subdirectory of the current directory.\n\n### Tests\n\nTo run them the first step is to configure the way to launch the orchestrator and the cli in a `.env` file.\n\nYou can copy `.env.template` for an example of what\'s expected.\n\n#### Module tests\n\nThese tests only rely on the sdk, no connection to an orchestrator is done.\n\nTo execute the module tests, simply run\n\n```\npoetry run task test\n```\n\n#### Integration tests\n\nThese tests launch and use an orchestrator they are slower but more in depth.\n\n##### Run in a docker image\n\nThis is the easiest way to run the tests.\n\n```\n./scripts/run_integration_test.sh\n```\n\nBy default it will use the latest public version `cogment/orchestrator` released on [DockerHub](https://hub.docker.com/u/cogment). To use specific versions define `COGMENT_ORCHESTRATOR_IMAGE`.\n\n```\n./scripts/run_integration_test.sh\n```\n\n##### Run locally\n\n```\npoetry run task test --launch-orchestrator\n```\n\nYou\'ll need to define:\n- Either `COGMENT_ORCHESTRATOR_IMAGE` (as above) or `COGMENT_ORCHESTRATOR` as the path to a locally built Cogment orchestrator executable.\n\n### Lint\n\nRun the linter using\n\n```\npoetry run task lint\n```\n\n### Check conflicting dependencies with "popular" Python packages\n\n```\n./scripts/check_dependencies_conflicts.sh\n```\n\nThis script will check for conflicts required by the cogment-py-sdk and the popular Python packages in the AI/ML/Data ecosystem.\n\n### Build the source package\n\nBuild the source package (this step will only be succesfull if `poetry install` succeeded)\n\n```\npoetry build -f sdist\n```\n\n### Release process\n\nPeople having mainteners rights of the repository can follow these steps to release a version **MAJOR.MINOR.PATCH**. The versioning scheme follows [Semantic Versioning](http://semver.org/spec/v2.0.0.html).\n\n1. Run `./scripts/create_release_branch.sh MAJOR.MINOR.PATCH` to create the release branch and update the version of the package,\n2. On the release branch, check and update the changelog if needed,\n3. Update `./.cogment-api.yaml` to use the public release of the API,\n4. Update `./.gitlab-ci.yml`, `integration_test`, and `COGMENT_ORCHESTRATOR_IMAGE` to match the latest public releases of the orchestrator and cli\n5. Make sure everything\'s fine on CI,\n6. Run `./scripts/tag_release.sh MAJOR.MINOR.PATCH` to create the specific version section in the changelog, merge the release branch in `main`, create the release tag and update the `develop` branch with those.\n\nThe rest, publishing the package to PyPI and updating the mirror repositories, is handled directly by the CI.\n',
    'author': 'Artificial Intelligence Redefined',
    'author_email': 'dev+cogment@ai-r.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cogment.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.10',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
