# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pacsanini',
 'pacsanini.cli',
 'pacsanini.dashboard',
 'pacsanini.db',
 'pacsanini.db.migrations',
 'pacsanini.db.migrations.versions',
 'pacsanini.io',
 'pacsanini.net',
 'pacsanini.pipeline']

package_data = \
{'': ['*'], 'pacsanini.dashboard': ['assets/*']}

install_requires = \
['PyYAML>=5.4',
 'SQLAlchemy-Utils>=0.37.8,<0.38.0',
 'SQLAlchemy[mypy]>=1.4.22,<2.0.0',
 'alembic>=1.7.4,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'dash>=2.0.0,<3.0.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.2.4,<2.0.0',
 'prefect>=0.15.6,<0.16.0',
 'pydantic>=1.7.4',
 'pydicom>=2.1.2,<3.0.0',
 'pynetdicom>=1.5.7,<2.0.0']

entry_points = \
{'console_scripts': ['pacsanini = pacsanini.cli:entry_point']}

setup_kwargs = {
    'name': 'pacsanini',
    'version': '0.2.1',
    'description': 'A package for DICOM utilities.',
    'long_description': "![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pacsanini)\n![PyPI](https://img.shields.io/pypi/v/pacsanini)\n![PyPI - Status](https://img.shields.io/pypi/status/pacsanini)\n[![Documentation Status](https://readthedocs.org/projects/pacsanini/badge/?version=latest)](https://pacsanini.readthedocs.io/en/latest/?badge=latest)\n![GitHub](https://img.shields.io/github/license/Therapixel/pacsanini)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Therapixel/pacsanini/pacsanini%20run%20tests%20for%20PR)\n![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Therapixel/pacsanini)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n\n# pacsanini\n\n`pacsanini` 🎻 is a package designed to help with the collection of DICOM files and the extraction\nof DICOM tags (metadata) for structuring purposes.\n\n`pacsanini`'s functionalities come out of a desire to facilitate research in\nmedical imagery by easing the process of data collection and structuring.\nThe two main pain points for this are:\n\n* acquiring data from a PACS\n* extracting metadata from DICOM files in research-ready formats (eg: csv)\n\nThe project seeks to target medical/research professionals that are not necessarily\nfamiliar with coding but wish to obtain data sets and software engineers that wish to\nbuild applications with a certain level of abstraction.\n\n## Documentation\n\nCheck out the complete documentation on [readthedocs](https://pacsanini.readthedocs.io/en/latest/).\nYou will be able to find examples on how to use the `pacsanini` API from within you Python application\nand as a command line tool.\n\n## Contributing and Code of Conduct\n\nAll contributions to improve `pacsanini` are welcome and valued. For more information on how you can contribute,\nplease read the [Contributing](CONTRIBUTING.md) document and make sure that you are familiar with our\n[Code of Conduct](CODE_OF_CONDUCT.md).\n\nYou are also more than welcome to open a discussion on our [GitHub discussions](https://github.com/Therapixel/pacsanini/discussions) page.\n\n## Installation\n\nTo install a particular release version, check out the available versions of `pacsanini` on [PyPI](https://pypi.org/project/pacsanini/)\nor simply run the following command to obtain the latest release:\n\n```bash\npip install pacsanini\n```\n\nTo obtain the cutting edge version of `pacsanini`, you can use `pip` or `poetry` in the following way:\n\n```bash\npip install git+https://github.com/Therapixel/pacsanini.git\n# or\npoetry add git+https://github.com/Therapixel/pacsanini.git\n```\n### For development\n\n`poetry` is the only supported build tool for installing `pacsanini` in a development context.\nSee the previous section on how to install `poetry`.\n\n```bash\ngit clone https://github.com/Therapixel/pacsanini.git\ncd pacsanini\npoetry install --no-root --no-dev\n# or, to install the project and its development dependencies:\npoetry install --no-root\n```\n\n### Usage with docker\n\nA docker image can be built locally to run `pacsanini` within an isolated environment.\n\n```bash\ndocker image build -t pacsanini:latest .\ndocker run pacsanini --help\n```\n\n## Roadmap\n\nThe following topics are the main areas where `pacsanini` can improve as a library and a tool.\nOf course, these topics are up for discussion and such discussions are encouraged in the\n[GitHub issues](https://github.com/Therapixel/pacsanini/issues) section.\n",
    'author': 'Aurélien Chick',
    'author_email': 'achick@therapixel.com',
    'maintainer': 'Aurélien Chick',
    'maintainer_email': 'achick@therapixel.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
