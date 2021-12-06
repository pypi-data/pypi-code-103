# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enex2notion']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'notion>=0.0.28,<0.0.29',
 'progress>=1.6,<2.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'tinycss2>=1.1.1,<2.0.0',
 'w3lib>=1.22.0,<2.0.0']

entry_points = \
{'console_scripts': ['enex2notion = enex2notion.cli:main']}

setup_kwargs = {
    'name': 'enex2notion',
    'version': '0.1.4',
    'description': 'Import Evernote ENEX files to Notion',
    'long_description': '# enex2notion\n\n[![PyPI version](https://img.shields.io/pypi/v/enex2notion?label=version)](https://pypi.python.org/pypi/enex2notion)\n[![Python Version](https://img.shields.io/pypi/pyversions/enex2notion.svg)](https://pypi.org/project/enex2notion/)\n[![tests](https://github.com/vzhd1701/enex2notion/actions/workflows/test.yml/badge.svg)](https://github.com/vzhd1701/enex2notion/actions/workflows/test.yml)\n[![codecov](https://codecov.io/gh/vzhd1701/enex2notion/branch/master/graph/badge.svg)](https://codecov.io/gh/vzhd1701/enex2notion)\n\nEasy way to import [Evernote\'s](https://www.evernote.com/) `*.enex` files to [Notion.so](https://notion.so)\n\nNotion\'s native Evernote importer doesn\'t do it for me, so I decided to write my own. Thanks to **Cobertos** and [md2notion](https://github.com/Cobertos/md2notion) for inspiration and **Jamie Alexandre** for [notion-py](https://github.com/jamalex/notion-py).\n\nYou can either use Evernote native export or try out my other tool, [evernote-backup](https://github.com/vzhd1701/evernote-backup), to export `*.enex` files from Evernote.\n\n### What is preserved\n\n- Embedded files and images are uploaded to Notion\n  - nested images will appear after paragraph\n- Text formatting (**bold**, _italic_, etc) and colors\n- Tables are converted to the new format (no colspans though)\n- Everything else basically\n\n### What is lost\n\n- Paragraph alignment\n- Subscript and superscript formatting\n- Custom fonts and font sizes\n- Tasks\n- Encrypted blocks\n  - just decrypt them before export\n- Web Clips\n  - you\'ll have better luck converting those to `*.md` and using [md2notion](https://github.com/Cobertos/md2notion)\n\n## Installation\n\n[**Download the latest binary release**](https://github.com/vzhd1701/enex2notion/releases/latest) for your OS.\n\n### With PIP\n\n```bash\n$ pip install enex2notion\n```\n\n**Python 3.6 or later required.**\n\nOr, since **enex2notion** is a standalone tool, it might be more convenient to install it using [**pipx**](https://github.com/pipxproject/pipx):\n\n```bash\n$ pipx install enex2notion\n```\n\n### From source\n\nThis project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.\n\n```shell\n$ git clone https://github.com/vzhd1701/enex2notion.git\n$ cd enex2notion/\n$ poetry install --no-dev\n$ poetry run enex2notion\n```\n\n## Usage\n\n```bash\n$ enex2notion --help\nusage: enex2notion [-h] [--token TOKEN] [--mode {DB,PAGE}] [--add-meta] [--done-file FILE] [--verbose] [--version] FILE/DIR [FILE/DIR ...]\n\nUploads ENEX files to Notion\n\npositional arguments:\n  FILE/DIR          ENEX files or directories to upload\n\noptional arguments:\n  -h, --help        show this help message and exit\n  --token TOKEN     Notion token, stored in token_v2 cookie for notion.so [NEEDED FOR UPLOAD]\n  --mode {DB,PAGE}  upload each ENEX as database (DB) or page with children (PAGE) (default: DB)\n  --add-meta        include metadata (created, tags, etc) in notes, makes sense only with PAGE mode\n  --done-file FILE  file for uploaded notes hashes to resume interrupted upload\n  --verbose         output debug information\n  --version         show program\'s version number and exit\n```\n\nYou can pass single `*.enex` files or directories. The program will recursively scan directories for `*.enex` files.\n\nThe upload requires you to have a `token_v2` cookie for the Notion website. For information on how to get it, see [this article](https://www.notion.so/Find-Your-Notion-Token-5da17a8df27a4fb290e9e3b5d9ba89c4).\n\nThe program can run without `--token` provided though. It will not make any network requests without it. Executing a dry run with `--verbose` is an excellent way to check if your `*.enex` files are parsed correctly before uploading.\n\nThe upload will take some time since each note is uploaded block-by-block, so you\'ll probably need some way of resuming it. `--done-file` is precisely for that. All uploaded note hashes will be stored there, so the next time you start, the upload will continue from where you left off.\n\nAll uploaded notebooks will appear under the automatically created `Evernote ENEX Import` page. The program will mark unfinished notes with `[UNFINISHED UPLOAD]` text in the title. After successful upload, the mark will be removed.\n\nThe `--mode` option allows you to choose how to upload your notebooks: as databases or pages. `DB` mode is the default since Notion itself uses this mode when importing from Evernote. `PAGE` mode makes the tree feel like the original Evernote notebooks hierarchy.\n\nSince `PAGE` mode does not benefit from having separate space for metadata, you can still preserve the note\'s original meta with the `--add-meta` option. It will attach a callout block with all meta info as a first block in each note.\n\n## Examples\n\n### Checking notes before upload\n\n```shell\n$ enex2notion --verbose my_notebooks/\nWARNING: No token provided, dry run mode. Nothing will be uploaded to Notion!\nINFO: Processing directory \'my_notebooks\'...\nINFO: Processing notebook \'Test Notebook\'...\nDEBUG: Parsing note \'Test note 1\'\nDEBUG: Parsing note \'Test note 2\'\nDEBUG: Parsing note \'Test note 3\'\nDEBUG: Parsing note \'Test note with encrypted block\'\nWARNING: Skipping encrypted block\n```\n\n### Uploading notes from a single notebook\n\n```shell\n$ enex2notion --token "30d0...9c12" "my_notebooks/Test Notebook.enex"\nINFO: \'Evernote ENEX Import\' page found\nINFO: Processing notebook \'Test Notebook\'...\nINFO: Creating new page for note \'Test note\'\nUploading \'Test note\' |####                            | 40/304\n```\n\n## Dependencies\n\n- [notion](https://github.com/jamalex/notion-py)\n- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)\n- [python-dateutil](https://github.com/dateutil/dateutil)\n- [progress](http://github.com/verigak/progress/)\n- [requests](https://github.com/psf/requests)\n- [w3lib](https://github.com/scrapy/w3lib)\n- [tinycss2](https://github.com/Kozea/tinycss2)\n',
    'author': 'vzhd1701',
    'author_email': 'vzhd1701@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vzhd1701/enex2notion',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
