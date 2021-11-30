# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qlacref_authorities']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'quality-lac-data-ref-authorities',
    'version': '2021.4',
    'description': 'This is a redistribution of the ONS dataset on Lower Tier Local Authority toUpper Tier Local Authority Lookup packaged for the Quality Lac Data project.Source: Office for National Statistics licensed under the Open Government Licence v.3.0',
    'long_description': '# Quality LAC Data Reference - Local Authority Data\n\nThis is a redistribution of the ONS dataset on **Lower Tier Local Authority to\nUpper Tier Local Authority (April 2021) Lookup in England and Wales** shaped \nto be used in the Quality Lac Data project.\n\nThis repository contains pypi and npm distributions of\nsubsets of this dataset as well as the scripts to\ngenerate them from source.\n\nSource: Office for National Statistics licensed under the Open Government Licence v.3.0\n\nRead more about this dataset here:\n\n* https://geoportal.statistics.gov.uk/datasets/ons::lower-tier-local-authority-to-upper-tier-local-authority-april-2021-lookup-in-england-and-wales/about\n\n## Regular updates\n\nWhen a new authority distribution is available, download it and add it to the source folder and\nat the same time delete the existing file from this location. There can only be one file\nin the source folder at a time.\n\nAfter updating the sources, run the script found in `bin/generate-output-files.py` to \nregenerate the output file.\n\nCommit everything to GitHub. If ready to make a release, make sure to update the version in \n[pyproject.toml](./pyproject.toml), push to GitHub and then create a GitHub release. The \n[GitHub Action](.github/workflows/python-publish.yml) will then create the distribution files and\nupload to [PyPI][pypi].\n\nRelease naming should follow a pseudo-[semantic versioning][semver] format:\n`<YEAR>.<MONTH>.<PATCH>`. Alpha and beta releases can be flagged by appending \n`-alpha.<number>` and `-beta.<number>`. \n\nFor example, the April 2021 release is named [2021.4][2021.4] with the associated tag [v2021.4][tag-v2021.4].\n\n[pypi]: https://pypi.org/project/quality-lac-data-ref-authorities/\n[semver]: https://semver.org/\n[2021.4]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-authorities/releases/tag/v2021.4\n[tag-v2021.4]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-authorities/tree/v2021.4\n',
    'author': 'Office for National Statistics',
    'author_email': 'sharedcustomercontactcentre@ons.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-authorities',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
