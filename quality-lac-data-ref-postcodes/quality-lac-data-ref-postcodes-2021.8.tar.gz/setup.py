# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qlacref_postcodes']

package_data = \
{'': ['*']}

install_requires = \
['rsa>=4.7']

setup_kwargs = {
    'name': 'quality-lac-data-ref-postcodes',
    'version': '2021.8',
    'description': 'This is a redistribution of the ONS dataset on Lower Tier Local Authority toUpper Tier Local Authority Lookup packaged for the Quality Lac Data project.Source: Office for National Statistics licensed under the Open Government Licence v.3.0',
    'long_description': '# Quality LAC Data Reference - Postcodes\n\nThis is a redistribution of the **ONS Postcode Directory** shaped\nto be used in the Quality Lac Data project.\n\nThis repository contains PyPI and npm distributions of\nsubsets of this dataset as well as the scripts to\ngenerate them from source.\n\nSource: Office for National Statistics licensed under the Open Government Licence v.3.0\n\nRead more about this dataset here:\n\n* https://geoportal.statistidcs.gov.uk/datasets/ons::ons-postcode-directory-august-2021/about\n\nTo keep distribution small, only pickled dataframes compatible \nwith pandas 1.0.5 are included. This will hopefully change\nonce we figure out how to do different versions as extras.\n\nAs pickle is inherently unsafe, the SHA-512 checksum for each file\nis included in [hashes.txt](qlacref_postcodes/hashes.txt). This\nfile is signed with [this key](./id_rsa.pub). \n\nWhen downloading from PyPI, specify the environment variable\n`QLACREF_PC_KEY` to either be the public key itself, or a path\nto where it can be loaded from. The checksums are then verified\nand each file checked before unpickling. \n\n## Regular updates\n\nWhen a new postcode distribution is available, download it and add it to the source folder and\nat the same time delete the existing file from this location. There can only be one file\nin the source folder at a time.\n\nAfter updating the postcode sources, run the script found in `bin/generate-output-files.py` to \nregenerate the output files for each letter of the alphabet. These end up in the \nqlacref_postcodes directory.\n\nTo sign the postcodes, you need the distribution private key. Run the script `bin/sign-files.py` to\ncreate the signed checksum file. \n\nCommit everything to GitHub. If ready to make a release, make sure to update the version in \n[pyproject.toml](./pyproject.toml), push to GitHub and then create a GitHub release. The \n[GitHub Action](.github/workflows/python-publish.yml) will then create the distribution files and\nupload to [PyPI][pypi].\n\n\n[pypi]: https://pypi.org/project/quality-lac-data-ref-postcodes/',
    'author': 'Office for National Statistics',
    'author_email': 'sharedcustomercontactcentre@ons.gov.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-postcodes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
