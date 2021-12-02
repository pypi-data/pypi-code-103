# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['immunopipe']

package_data = \
{'': ['*'], 'immunopipe': ['reports/*', 'scripts/*']}

install_requires = \
['biopipen>=0.1,<0.2',
 'datar>=0.5,<0.6',
 'pipen-args>=0.1.3,<0.2.0',
 'pipen-filters>=0.0,<0.1',
 'pipen-report>=0.0,<0.1']

entry_points = \
{'console_scripts': ['immunopipe = immunopipe.pipeline:main']}

setup_kwargs = {
    'name': 'immunopipe',
    'version': '0.0.2',
    'description': 'A pipeline for integrative analysis for scTCR- and scRNA-seq data',
    'long_description': '# immunopipe\n\nIntegrative analysis for scTCR- and scRNA-seq data\n\n## Requirements & Installation\n\n- `python`: `3.7+`\n    - Other python depedencies should be installed via `pip install -U immunopipe`\n\n- `R`\n  - `immunarch`: `v0.6.7+`\n  - `Seurat`: `v4.0+`\n  - `dplyr`\n  - `tidyr`\n  - `tibble`\n  - `ggplot2`\n  - `ggradar`\n  - `ggprism`\n  - `ggrepel`\n  - `future`\n  - `parallel`\n  - `enrichR`\n  - `ComplexHeatmap`\n\n- Other\n  - VDJtools: https://vdjtools-doc.readthedocs.io/en/master/install.html\n\n## Modules\n\n- Basic TCR data analysis using `immunarch`\n- Clone Residency analysis if you have paired samples (i.e. Tumor vs Normal)\n- V-J usage, the frequency of various V-J junctions in circos-style plots\n- Clustering cells and configurale arguments to separate T and non-T cells\n- Clustering T cell, markers for each cluster and enrichment analysis for the markers\n- Radar plots to show the composition of cells for clusters\n- Markers finder for selected groups of cells\n- Expression investigation of genes of interest for selected groups of cells\n- UMAPs\n\n## Documentaion\n\nhttps://pwwang.github.io/immunopipe\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/immunopipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
