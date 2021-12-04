# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['micone',
 'micone.config',
 'micone.conversion',
 'micone.logging',
 'micone.main',
 'micone.pipelines',
 'micone.pipelines.templates.denoise_cluster.chimera_checking',
 'micone.pipelines.templates.denoise_cluster.otu_assignment',
 'micone.pipelines.templates.network_inference.bootstrap',
 'micone.pipelines.templates.network_inference.correlation',
 'micone.pipelines.templates.network_inference.direct',
 'micone.pipelines.templates.network_inference.network',
 'micone.pipelines.templates.otu_processing.export',
 'micone.pipelines.templates.otu_processing.transform',
 'micone.pipelines.templates.sequence_processing.trimming',
 'micone.pipelines.templates.tax_assignment.assign',
 'micone.setup',
 'micone.utils',
 'micone.validation']

package_data = \
{'': ['*'],
 'micone.pipelines': ['configs/*',
                      'envs/micone-cozine/*',
                      'envs/micone-dada2/*',
                      'envs/micone-flashweave/*',
                      'envs/micone-harmonies/*',
                      'envs/micone-mldm/*',
                      'envs/micone-propr/*',
                      'envs/micone-qiime2/*',
                      'envs/micone-sparcc/*',
                      'envs/micone-spieceasi/*',
                      'envs/micone-spring/*',
                      'functions/*',
                      'modules/denoise_cluster/*',
                      'modules/denoise_cluster/chimera_checking/*',
                      'modules/denoise_cluster/otu_assignment/*',
                      'modules/network_inference/*',
                      'modules/network_inference/bootstrap/*',
                      'modules/network_inference/correlation/*',
                      'modules/network_inference/direct/*',
                      'modules/network_inference/network/*',
                      'modules/otu_processing/*',
                      'modules/otu_processing/export/*',
                      'modules/otu_processing/transform/*',
                      'modules/sequence_processing/*',
                      'modules/sequence_processing/demultiplexing/*',
                      'modules/sequence_processing/trimming/*',
                      'modules/tax_assignment/*',
                      'modules/tax_assignment/assign/*',
                      'modules/utils/*',
                      'templates/sequence_processing/demultiplexing/*']}

install_requires = \
['Jinja2>=2.11.2,<3.0.0',
 'biom-format>=2.1.10,<3.0.0',
 'click>=7.1.2,<8.0.0',
 'ete3>=3.1.2,<4.0.0',
 'h5py>=3.1.0,<4.0.0',
 'halo>=0.0.31,<0.0.32',
 'jinja2schema>=0.1.4,<0.2.0',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib>=3.3.3,<4.0.0',
 'networkx>=2.5,<3.0',
 'numpy>=1.19.4,<2.0.0',
 'pandas>=1.2.0,<2.0.0',
 'schematics>=2.1.0,<3.0.0',
 'simplejson>=3.17.2,<4.0.0',
 'statsmodels>=0.12.1,<0.13.0',
 'toml>=0.10.2,<0.11.0']

extras_require = \
{'docs': ['Sphinx>=3.4.2,<4.0.0', 'sphinx-rtd-theme>=0.5.1,<0.6.0']}

entry_points = \
{'console_scripts': ['micone = micone.cli:main']}

setup_kwargs = {
    'name': 'micone',
    'version': '0.10.4',
    'description': 'The Microbial Co-occurrence Network Explorer',
    'long_description': '# MiCoNE - Microbial Co-occurrence Network Explorer\n\n![Build Status](https://github.com/segrelab/MiCoNE/workflows/build/badge.svg)\n[![Documentation Status](https://readthedocs.org/projects/micone/badge/?version=latest)](https://micone.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/segrelab/MiCoNE/branch/master/graph/badge.svg?token=2tKiI0lUJb)](https://codecov.io/gh/segrelab/MiCoNE)\n[![CodeFactor](https://www.codefactor.io/repository/github/segrelab/micone/badge)](https://www.codefactor.io/repository/github/segrelab/micone)\n[![Updates](https://pyup.io/repos/github/segrelab/MiCoNE/shield.svg)](https://pyup.io/repos/github/segrelab/MiCoNE/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n`MiCoNE`, is a flexible and modular pipeline for 16S data analysis.\nIt incorporates various popular, publicly available tools as well as custom Python modules and scripts to facilitate inference of co-occurrence networks from 16S data.\n\n<div align="center">\n⚠️ <p><strong>The package is under active development and breaking changes are possible</strong></p>\n</div>\n\n-   Free software: MIT license\n-   Documentation: <https://micone.readthedocs.io/>\n\nManuscript can be found on [bioRxiv](https://www.biorxiv.org/content/10.1101/2020.09.23.309781v2)\n\n## Features\n\n-   Plug and play architecture: allows easy additions and removal of new tools\n-   Flexible and portable: allows running the pipeline on local machine, compute cluster or the cloud with minimal configuration change. Uses the [nextflow](www.nextflow.io) under the hood\n-   Parallelization: automatic parallelization both within and across samples (needs to be enabled in the `config` file)\n-   Ease of use: available as a minimal `Python` library (without the pipeline) or the full `conda` package\n\n## Installation\n\nInstalling the minimal `Python` library:\n\n```sh\npip install micone\n```\n\nInstalling the `conda` package:\n\n```sh\ngit clone https://github.com/segrelab/MiCoNE.git\ncd MiCoNE\nconda env create -n micone -f env.yml\npip install .\n```\n\n> NOTE:\n> The `conda` package is currently being updated and will be available soon.\n\n## Workflow\n\n![pipeline](assets/pipeline.png)\n\nIt supports the conversion of raw 16S sequence data or counts matrices into co-occurrence networks through multiple methods. Each process in the pipeline supports alternate tools for performing the same task, users can use the configuration file to change these values.\n\n## Usage\n\nThe `MiCoNE` pipelines comes with an easy to use CLI. To get a list of subcommands you can type:\n\n```bash\nmicone --help\n```\n\nSupported subcommands:\n\n1. `init` - Creates `conda` environments for various pipeline processes\n2. `run` - The main subcommand that runs the pipeline\n3. `clean` - Cleans temporary data, log files and other extraneous files\n\nTo run the pipeline:\n\n```bash\nmicone run -p local -c run.toml -m 4\n```\n\nThis runs the pipeline in the `local` machine using `run.toml` for the pipeline configuration and with a maximum of 4 processes in parallel at a time.\n\n## Configuration\n\nThe configuration of the pipeline can be done using a `.toml` file.\nThe details can be found in the relevant section in the docs.\nHere is an example `config` file that performs:\n\n1. grouping of OTUs by taxonomy level\n2. correlation of the taxa using `fastspar`\n3. calculates p-values\n4. constructs the networks\n\n```toml\ntitle = "A example pipeline for testing"\n\norder = """\n  otu_processing.filter.group\n  otu_processing.export.biom2tsv\n  network_inference.bootstrap.resample\n  network_inference.correlation.sparcc\n  network_inference.bootstrap.pvalue\n  network_inference.network.make_network_with_pvalue\n"""\n\noutput_location = "/home/dileep/Documents/results/sparcc_network"\n\n[otu_processing.filter.group]\n  [[otu_processing.filter.group.input]]\n    datatype = "otu_table"\n    format = ["biom"]\n    location = "correlations/good/deblur/deblur.biom"\n  [[otu_processing.filter.group.parameters]]\n    process = "group"\n    tax_levels = "[\'Family\', \'Genus\', \'Species\']"\n\n[otu_processing.export.biom2tsv]\n\n[network_inference.bootstrap.resample]\n  [[network_inference.bootstrap.resample.parameters]]\n    process = "resample"\n    bootstraps = 10\n\n[network_inference.correlation.sparcc]\n  [[network_inference.correlation.sparcc.parameters]]\n    process = "sparcc"\n    iterations = 5\n\n[network_inference.bootstrap.pvalue]\n\n[network_inference.network.make_network_with_pvalue]\n  [[network_inference.network.make_network_with_pvalue.input]]\n    datatype = "metadata"\n    format = ["json"]\n    location = "correlations/good/deblur/deblur_metadata.json"\n  [[network_inference.network.make_network_with_pvalue.input]]\n    datatype = "computational_metadata"\n    format = ["json"]\n    location = "correlations/good/deblur/deblur_cmetadata.json"\n```\n\nOther example `config` files can be found at `tests/data/pipelines`\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.\n',
    'author': 'Dileep Kishore',
    'author_email': 'dkishore@bu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/segrelab/MiCoNE',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
