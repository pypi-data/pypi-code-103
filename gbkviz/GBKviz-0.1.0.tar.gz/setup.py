# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gbkviz', 'gbkviz.scripts']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0', 'reportlab>=3.6.2,<4.0.0', 'streamlit>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['download_gbk_from_acc = '
                     'gbkviz.scripts.download_gbk_from_acc:main',
                     'gbkviz_webapp = '
                     'gbkviz.scripts.launch_gbkviz_webapp:main']}

setup_kwargs = {
    'name': 'gbkviz',
    'version': '0.1.0',
    'description': 'Genbank data visualization webapp',
    'long_description': '# GBKviz: Genbank Data Visuzalization tool\n\n## Overview\n\nGBKviz is browser-based Genbank data vizualization webapp.  \nUser can easily and flexibly plot specified region genome CDS figure in any format.  \nIn addition, GBKvis can perform comparative genome plot figure.  \n\nDemo GIF here...\n\n## Install\n\nGBKviz is implemented with Python3 (Tested on Ubuntu20.04)\n\nInstall PyPI stable version with pip:\n\n    pip install gbkviz\n\nInstall latest development version with pip:\n\n    pip install git+git://github.com/moshi4/GBKviz.git\n\n### Dependencies\n\n- [Streamlit](https://streamlit.io/)  \n  Web app framework for quick development\n\n- [BioPython](https://github.com/biopython/biopython)  \n  Utility tools for computational molecular biology\n\n- [MUMmer](https://github.com/mummer4/mummer) (Optional)  \n  Genome alignment tool for comparative genomics (v3 or v4)\n  \n## Command Usage\n\nLaunch GBKviz in web browser:\n\n    gbkviz_webapp\n\n## Usage\n',
    'author': 'moshi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moshi4/GBKviz/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
