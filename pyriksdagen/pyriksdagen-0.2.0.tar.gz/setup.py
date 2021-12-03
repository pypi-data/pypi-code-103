# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['pyriksdagen']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyriksdagen',
    'version': '0.2.0',
    'description': 'Access the Riksdagen corpus',
    'long_description': '# Swedish parliamentary proceedings - Riksdagens protokoll 1921-2021 v0.3.0\n\n_Westac Project, 2020-2021_\n\nThe full data set consists of multiple parts:\n\n- Riksdagens protokoll between from 1921 until today in the [Parla-clarin](https://github.com/clarin-eric/parla-clarin) format\n- Comprehensive list of MPs and cabinet members during this period\n- Traceable logs of all curation and segmentation as a git history\n- [Documentation](https://github.com/welfare-state-analytics/riksdagen-corpus/wiki/) of the corpus and the curation process\n- [A Google Colab notebook](https://colab.research.google.com/drive/1C3e2gwi9z83ikXbYXNPfB6RF7spTgzxA?usp=sharing) that demonstrates how the dataset can be used with Python\n\n## Basic use\n\nA full dataset is available under [this download link](https://github.com/welfare-state-analytics/riksdagen-corpus/releases/download/v0.3.0-alpha/corpus.zip). It has the following structure\n\n- Annual protocol files in the ```corpus/``` folder\n- List of MPs ```corpus/members_of_parliament.csv```\n- List of ministers ```corpus/ministers.csv```\n- List of speakers of the house ```corpus/talman.csv```\n\nThe workflow to use the data is demonstrated in [this Google Colab notebook](https://colab.research.google.com/drive/1C3e2gwi9z83ikXbYXNPfB6RF7spTgzxA?usp=sharing).\n\n## Participate in the curation process\n\nThe corpora are large and automatically curated and segmented. If you find any errors, it is possible to submit corrections to them. This is documented in the [project wiki](https://github.com/welfare-state-analytics/riksdagen-corpus/wiki/Submit-corrections).\n',
    'author': 'ninpnin',
    'author_email': 'vainoyrjanainen@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/welfare-state-analytics/riksdagen-corpus',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
