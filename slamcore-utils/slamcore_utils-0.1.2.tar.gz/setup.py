# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slamcore_utils', 'slamcore_utils.scripts']

package_data = \
{'': ['*'], 'slamcore_utils': ['share/*', 'share/capture_infos/*']}

install_requires = \
['numpy>=1.21.4,<2.0.0', 'questionary>=1.10.0,<2.0.0']

extras_require = \
{'tqdm': ['tqdm>=4.62.3,<5.0.0']}

entry_points = \
{'console_scripts': ['slamcore-convert-openloris = '
                     'slamcore_utils.scripts.convert_openloris:main',
                     'slamcore-setup-dataset = '
                     'slamcore_utils.scripts.setup_dataset:main']}

setup_kwargs = {
    'name': 'slamcore-utils',
    'version': '0.1.2',
    'description': 'SLAMcore SLAM Utilities',
    'long_description': '# slamcore_utils\n\n<a href="https://github.com/slamcore/slamcore_utils/actions" alt="CI">\n<img src="https://github.com/slamcore/slamcore_utils/actions/workflows/ci.yml/badge.svg" /></a>\n\n<a href="https://github.com/slamcore/slamcore_utils/blob/master/LICENSE.md" alt="LICENSE">\n<img src="https://img.shields.io/github/license/slamcore/slamcore_utils.svg" /></a>\n<a href="https://pypi.org/project/slamcore_utils/" alt="pypi">\n<img src="https://img.shields.io/pypi/pyversions/slamcore_utils.svg" /></a>\n<a href="https://github.com/slamcore/slamcore_utils/actions" alt="lint">\n<img src="https://img.shields.io/badge/checks-mypy%2C%20pyright-brightgreen" /></a>\n<a href="https://badge.fury.io/py/slamcore_utils">\n<img src="https://badge.fury.io/py/slamcore_utils.svg" alt="PyPI version" height="18"></a>\n<!-- <a href="https://pepy.tech/project/slamcore_utils"> -->\n<!-- <img alt="Downloads" src="https://pepy.tech/badge/slamcore_utils"></a> -->\n<a href="https://github.com/psf/black">\n<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n\n## Description\n\n<!-- Change this when we add more scripts -->\n\nThis repo contains the `slamcore-setup-dataset` script. It can be used for\ninstalling a sample dataset for offline testing and evaluation of [SLAMcore][slamcore]\'s\nLocalization and Mapping capabilities.\n\nCurrently the following types of datasets are supported:\n\n- [EuRoC MAV Datasets](https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets)\n- [OpenLORIS-Scene Datasets](https://lifelong-robotic-vision.github.io/dataset/scene)\n- [TUM VI Datasets](https://vision.in.tum.de/data/datasets/visual-inertial-dataset)\n\n## Usage\n\nAfter [installation](#installation) the script should be available in your path.\nExecuting it will guide you through a list of questions in order to properly\nsetup a sample SLAM dataset.\n\nHere is a sample execution of the said script to enable processing of the `TUM-VI`\n`dataset-room4_1024_16`\n\n![setup-dataset2](https://github.com/slamcore/slamcore_utils/raw/master/share/images/slamcore-setup-dataset2.gif)\n\nHere\'s the same execution for the `OpenLORIS` `cafe1-1` dataset\n\n![setup-dataset1](https://github.com/slamcore/slamcore_utils/raw/master/share/images/slamcore-setup-dataset1.gif)\n\nAnd here\'s the execution guiding the user to the right download page, when\nthe datasets are not available locally yet.\n\n![setup-dataset3](https://github.com/slamcore/slamcore_utils/raw/master/share/images/slamcore-setup-dataset3.gif)\n\n## Installation\n\nInstall it directly from PyPI:\n\n```sh\npip3 install --user --upgrade slamcore_utils[tqdm]\n\n# Or if you don\'t want tqdm\'s polished progress bars\npip3 install --user --upgrade slamcore_utils\n```\n\n<details>\n  <summary>I don\'t want to have to install it</summary>\n\nMake sure the project dependencies are installed:\n\n`pip3 install -r requirements.txt`\n\nThen adjust your `PYTHONPATH` variable and run accordingly:\n\n```sh\ngit clone https://github.com/slamcore/slamcore_utils\ncd slamcore_utils\nexport PYTHONPATH=$PYTHONPATH:$PWD\n./slamcore_utils/scripts/setup_dataset.py\n```\n\n</details>\n\n<details>\n  <summary>I don\'t want to install any of your dependencies in my user\'s install directory</summary>\n\nConsider using either [pipx](https://github.com/pypa/pipx) or\n[poetry](https://github.com/python-poetry/poetry) to install this package and\nits dependencies isolated in a virtual environment:\n\n```sh\ngit clone https://github.com/slamcore/slamcore_utils\npoetry install\npoetry shell\n\n# the executables should now be available in your $PATH\nsetup-dataset\n```\n\n</details>\n\n## About SLAMcore\n\n[SLAMcore][slamcore] offers commercial-grade visual-inertial\nsimultaneous localisation and mapping (SLAM) software for real-time autonomous\nnavigation on robots and drones. [Request\naccess](https://www.slamcore.com/sdk-access) today to get started.\n\n\n[slamcore]: https://www.slamcore.com/\n',
    'author': 'Nikos Koukis',
    'author_email': 'nikolaos@slamcore.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/slamcore/slamcore_utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
