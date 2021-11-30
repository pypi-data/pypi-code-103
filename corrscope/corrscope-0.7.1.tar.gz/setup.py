# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corrscope',
 'corrscope.gui',
 'corrscope.settings',
 'corrscope.utils',
 'corrscope.utils.scipy']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.4,<6.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'atomicwrites>=1.4.0,<2.0.0',
 'attrs>=21.2.0,<22.0.0',
 'click>=8.0.1,<9.0.0',
 'matplotlib>=3.1,<4.0',
 'numpy>=1.15,<2.0',
 'ruamel.yaml>=0.17,<0.18']

entry_points = \
{'console_scripts': ['corr = corrscope.cli:main']}

setup_kwargs = {
    'name': 'corrscope',
    'version': '0.7.1',
    'description': 'Python program to render wave files into oscilloscope views, featuring advanced correlation-based triggering algorithm',
    'long_description': '# Corrscope\n\n[![Appveyor build status](https://ci.appveyor.com/api/projects/status/awiajnwd6a4uhu37/branch/master?svg=true)](https://ci.appveyor.com/project/nyanpasu64/corrscope/branch/master)\n[![Latest release](https://img.shields.io/github/v/release/corrscope/corrscope?include_prereleases)](https://github.com/corrscope/corrscope/releases)\n[![PyPI release](https://img.shields.io/pypi/v/corrscope.svg)](https://pypi.org/project/corrscope/)\n[![codecov](https://codecov.io/gh/corrscope/corrscope/branch/master/graph/badge.svg)](https://codecov.io/gh/corrscope/corrscope)\n\nCorrscope renders oscilloscope views of WAV files recorded from chiptune (game music from retro sound chips).\n\nCorrscope uses "waveform correlation" to track complex waves (including SNES and Sega Genesis/FM synthesis) which jump around on other oscilloscope programs.\n\nSample results can be found on my Youtube channel at https://www.youtube.com/nyanpasu64/videos.\n\nDocumentation is available at https://corrscope.github.io/corrscope/.\n\n![Screenshot of Corrscope and video preview](docs/images/corrscope-screenshot.png?raw=true)\n\n## Status\n\nCorrscope is currently in maintenance mode until further notice. The program basically works, but I may not respond to issues. For technical support, contact me at Discord (https://discord.gg/CCJZCjc), or alternatively in the issue tracker (using the "Support/feedback" template). Pull requests may be accepted if they\'re clean.\n\n## Dependencies\n\n- FFmpeg\n\n## Installation\n\n- Releases (recommended): https://github.com/corrscope/corrscope/releases\n- Dev Builds: https://ci.appveyor.com/project/nyanpasu64/corrscope/history\n\nOn Windows, download Windows binary releases (.7z files), then double-click `corrscope.exe` or run `corrscope (args)` via CLI.\n\nOn other operating systems, download cross-platform Python packages (.whl or .tar.gz), then install Python 3.6+ and run `pip install FILENAME.whl`, then run `corr (args)`.\n\n## Installing from PyPI via Pip (cross-platform, releases)\n\nInstall Python 3.6 or above (3.5 will not work). Note that Python versions other than 3.8 and 3.9 are untested.\n\n```shell\n# Installs into per-user Python environment.\npip3 install --user corrscope\ncorr (args)\n```\n\n## Running from Source Code (cross-platform, dev master)\n\nInstall Python 3.6 or above (3.5 will not work), and Poetry.\n\n```shell\n# Installs into an isolated environment.\n# Install Poetry (only do this once)\ncurl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python\ncd path/to/corrscope\npoetry install corrscope  # --develop is implied\npoetry run corr (args)\n```\n\n## GUI Tutorial\n\n1. Open GUI:\n    - `corrscope.exe` to create new project\n    - `corrscope.exe file.yaml` to open existing project\n1. Add audio to play back\n    - On the right side of the window, click "Browse" to pick a master audio file.\n1. Add oscilloscope channels\n    - On the right side of the window, click "Add" to add WAV files to be viewed.\n1. Edit settings\n    - Global settings on the left side of the window\n    - Per-channel on the right side\n1. Play or render to MP4/etc. video (requires ffmpeg)\n    - Via toolbar or menu\n\n## Command-line Tutorial\n\n1. Create YAML:\n    - `corrscope split*.wav --audio master.wav -w`\n    - Specify all channels on the command line.\n    - `-a` or `--audio` specifies master audio track.\n    - Creates file `master.yaml`.\n\n1. Edit `master.yaml` to change settings.\n\n1. Play (requires ffmpeg):\n    - `corrscope master.yaml -p/--play`\n\n1. Render and encode video (requires ffmpeg)\n    - `corrscope master.yaml -r/--render file.mp4` (other file extensions supported)\n\n## Contributing\n\nIssues, feature requests, and pull requests are accepted.\n\nThis project uses [Black code formatting](https://github.com/ambv/black). Either pull request authors can reformat code before creating a PR, or maintainers can reformat code before merging.\n\nYou can install a Git pre-commit hook to apply Black formatting before each commit. Open a terminal/cmd in this repository and run:\n\n```sh\npip install --user pre-commit\npre-commit install\n```\n',
    'author': 'nyanpasu64',
    'author_email': 'nyanpasu64@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/corrscope/corrscope/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
