# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kubedownscaler']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'kubernetes>=19.15.0,<20.0.0']

entry_points = \
{'console_scripts': ['kubectl-downscale = kubedownscaler.main:main']}

setup_kwargs = {
    'name': 'kubedownscaler',
    'version': '0.2.0',
    'description': 'Scale down and restore Kubernetes deployments and statefulsets',
    'long_description': "# kubedownscaler\n\nScales down Kubernetes Deployments and StatefulSets to 0 replicas, keeps note of the number\nof replicas in annotations, and scales everything back up to the original number of replicas.\n\nCan operate on a single namespace, or the entire cluster.\n\nIdeal for performing a controlled shutdown, maintenance, etc.\n\nUses whatever context your local `kubectl` has.\n\n## Install\n\n```sh\npip install kubedownscaler\n```\n\n## Use\n\nEither `-d|--down` or `-u|--up` must be specified.\n\n```\nusage: kubectl downscale [-h] (-d | -u) [--dry-run] [-n NAMESPACE] [--deployments | --no-deployments]\n               [--statefulsets | --no-statefulsets]\n\noptions:\n  -h, --help            show this help message and exit\n  -d, --down            scale down cluster resources\n  -u, --up              scale up to restore state\n  --dry-run             don't actually scale anything\n  -n NAMESPACE, --namespace NAMESPACE\n                        namespace to operate on\n  --deployments, --no-deployments\n                        scale Deployments (default: True)\n  --statefulsets, --no-statefulsets\n                        scale StatefulSets (default: True)\n```\n\n## Build\n\n```sh\npoetry install\npoetry build\npoetry publish\n```\n",
    'author': 'Jonathan Gazeley',
    'author_email': 'me@jonathangazeley.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/djjudas21/kubedownscaler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
