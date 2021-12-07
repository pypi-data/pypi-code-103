# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ways_py']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.8.0,<2.0.0',
 'altair-saver>=0.5.0,<0.6.0',
 'altair>=4.1.0,<5.0.0',
 'certifi>=2021.10.8,<2022.0.0',
 'importlib-metadata>=4.8.1,<5.0.0',
 'ipykernel>=6.4.1,<7.0.0',
 'ipython>=7.29.0,<8.0.0',
 'ipywidgets>=7.6.5,<8.0.0',
 'jsonschema==3.2.0',
 'jupyter>=1.0.0,<2.0.0',
 'nbmake>=0.8,<0.9',
 'pdocs>=1.1.1,<2.0.0',
 'pytest>=6.2.5,<7.0.0',
 'selenium>=4.0.0,<5.0.0',
 'vega-datasets>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'ways-py',
    'version': '0.1.1',
    'description': 'WAYS package for Python developed at University of Warwick and The Alan Turing Institute.',
    'long_description': "<!-- badges: start -->\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/WarwickCIM/ways-py/develop)\n[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n<!-- badges: end -->\n\n# _WAYS: What Aren't You Seeing_\n\nPython package for the [WAYS](https://www.turing.ac.uk/research/research-projects/ways-what-arent-you-seeing) project. See [API documentation](https://warwickcim.github.io/ways-py/).\n<!-- badges: start -->\n[![Publish](https://github.com/WarwickCIM/ways-py/actions/workflows/publish.yml/badge.svg?branch=release)](https://github.com/WarwickCIM/ways-py/actions/workflows/publish.yml)\n[![Build](https://github.com/WarwickCIM/ways-py/actions/workflows/build.yml/badge.svg?branch=develop)](https://github.com/WarwickCIM/ways-py/actions/workflows/build.yml)\n[![Docs](https://github.com/WarwickCIM/ways-py/actions/workflows/docs.yml/badge.svg?branch=develop)](https://github.com/WarwickCIM/ways-py/actions/workflows/docs.yml)\n<!-- badges: end -->\n\n“As you can see in figure 1…” may well be the most frequently made claim in science. But unlike claims concerning data, statistics, models and algorithms, those relating to visualisations are rarely evaluated or verified. So how can data scientists understand visualisations’ effectiveness and expressiveness? What is the visualisation equivalent of q-q plots, R^2 and K-folds tests?\n\nDesigning effective visualisations goes far beyond selecting a graph, scales and a ‘pretty’ style. Effective visualisations must negotiate sensitivities and interactions between visual elements (e.g. encodings, coordinate systems, guides, annotations), data (e.g. characteristics, transformations, partitions), and the discriminator function, which in this case is the perceptual and cognitive systems of humans. Despite their criticality, these methodological and design considerations are rarely surfaced, limiting the value extracted from visualisations. What does figure 1 actually visualise?\n\nThe ‘What Aren’t You Seeing’ (WAYS) project addresses 1) what we aren’t seeing in visualisations by 2) revealing the relevant knowledge, theory and practices that we are not seeing at the site of visualisation production. Our final goal is the WAYS package/library in which the properties, outcomes and affordances of visualisation designs are depicted through visualisations; a concept we term ‘Precursor Visualisations’. WAYS then addresses the challenge of generating a productive interplay between everyday visualisation work and the epistemology, practice, communication techniques and evaluation methods that should inform visualisation design at source (Robinson). To achieve this, we propose three work packages (WP1-3).\n\n# Quick start\n\nInstall from [PyPI](https://pypi.org/project/ways-py/) using `pip install ways-py`.\n\n## Development\n\nTo create the development environment, do the following:\n\n1. Install python poetry by following the [install instructions](https://python-poetry.org/docs/)\n2. From the top level dir: `poetry shell`\n - Note: your machine will need python 3.9 available - [install from here](https://www.python.org/downloads/release/python-397/) if you don't have it\n\n# Emojis on commit messages\n\nWe use a number of `git` [aliases](/.gitconfig.aliases) to track different kinds of commit; to use these yourself, add an `[include]` section to your [`.gitconfig`](https://git-scm.com/docs/git-config).\n",
    'author': 'Ed Chalstrey',
    'author_email': 'echalstrey@turing.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WarwickCIM/ways-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.9.9',
}


setup(**setup_kwargs)
