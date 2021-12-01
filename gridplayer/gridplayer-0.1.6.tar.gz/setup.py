# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gridplayer',
 'gridplayer.dialogs',
 'gridplayer.main',
 'gridplayer.multiprocess',
 'gridplayer.player',
 'gridplayer.player.managers',
 'gridplayer.utils',
 'gridplayer.widgets']

package_data = \
{'': ['*']}

install_requires = \
['PyQt5>=5.15.4,<6.0.0', 'pydantic>=1.8.2,<2.0.0', 'python-vlc==3.0.11115']

extras_require = \
{':sys_platform == "darwin"': ['pyobjc-core', 'pyobjc-framework-Cocoa']}

entry_points = \
{'console_scripts': ['gridplayer = gridplayer.__main__:main']}

setup_kwargs = {
    'name': 'gridplayer',
    'version': '0.1.6',
    'description': 'Play videos side-by-side',
    'long_description': '![GridPlayer](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/logo.png)\n\n[![GitHub release (latest by date)](https://img.shields.io/github/v/release/vzhd1701/gridplayer)](https://github.com/vzhd1701/gridplayer/releases/latest)\n[![PyPI version](https://img.shields.io/pypi/v/gridplayer)](https://pypi.python.org/pypi/gridplayer)\n\n## Screenshots\n\n[![Screenshot 1](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-001-thumb.png)](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-001.png)\n[![Screenshot 2](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-002-thumb.png)](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-002.png)\n[![Screenshot 3](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-003-thumb.png)](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-003.png)\n\n## About\n\nSimple VLC-based media player that can play multiple videos at the same time. You can\nplay as many videos as you like, the only limit is your hardware. It supports all video\nformats that VLC supports (which is all of them). You can save your playlist retaining\ninformation about the position, sound volume,  loops, aspect ratio, etc.\n\n## Features\n\n- Cross-platform (Linux, Mac, and Windows)\n- Support for any video format (VLC)\n- Hardware & software video decoding\n- Control video aspect, playback speed, zoom\n- Set loop fragments with frame percision\n- Configurable grid layout\n- Easy swap videos with drag-n-drop\n- Playlist retains settings for each video\n\n## Installation\n\n### Windows\n\n[![Download Windows Installer](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_windows_installer.png)](https://github.com/vzhd1701/gridplayer/releases/download/v0.1.6/GridPlayer-0.1.6-win64-install.exe)\n[![Download Windows Portable](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_windows_portable.png)](https://github.com/vzhd1701/gridplayer/releases/download/v0.1.6/GridPlayer-0.1.6-win64-portable.zip)\n\n### Linux\n\n[![Get it from the Flathub](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_flathub.png)](https://flathub.org/apps/details/com.vzhd1701.gridplayer)\n[![Get it from the Snap Store](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_snap.png)](https://snapcraft.io/gridplayer)\n[![Download AppImage](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_appimage.png)](https://github.com/vzhd1701/gridplayer/releases/download/v0.1.6/GridPlayer-0.1.6-x86_64.AppImage)\n\n**For better system integration install via Flathub.**\n\n#### Note on AppImage\n\nYou may need to set execute permissions on AppImage file in order to run it:\n\n```shell\n$ chmod +x GridPlayer-0.1.6-x86_64.AppImage\n```\n\n### MacOS\n\n[![Download DMG](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/dl_dmg.png)](https://github.com/vzhd1701/gridplayer/releases/download/v0.1.6/GridPlayer.0.1.6.dmg)\n\n**DMG image is not signed.** You will have to add an exception to run this app.\n\n- [How to open an app that hasn’t been notarized or is from an unidentified developer](https://support.apple.com/en-euro/HT202491)\n- [Open a Mac app from an unidentified developer](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unidentified-developer-mh40616/mac)\n\n### PIP\n\n```shell\n$ pip install -U gridplayer\n```\n\n**Python 3.8 or later required.**\n\nThis type of installation will also require a `vlc` package present in your system.\nPlease refer to [VLC official page](https://www.videolan.org/vlc/) for instructions on how to install it.\n\nSome distros (e.g. Ubuntu) might also require `libxcb-xinerama0` package.\n\n### From source\n\nThis project uses [poetry](https://python-poetry.org/) for dependency management and packaging. You will have to install it first. See [poetry official documentation](https://python-poetry.org/docs/) for instructions.\n\n```shell\n$ git clone https://github.com/vzhd1701/gridplayer.git\n$ cd gridplayer/\n$ poetry install --no-dev\n$ poetry run gridplayer\n```\n\nThe same notes about the Python version and external packages from **PIP** installation apply here.\n\n## Known issues\n\n#### Linux (Snap): [X screen](https://raw.githubusercontent.com/vzhd1701/gridplayer/master/resources/public/screenshot-x.png) when opening a file from the mounted disk\n\nYou need to allow GridPlayer snap to access removable storage devices via Snap Store or by running:\n\n```shell\n$ sudo snap connect gridplayer:removable-media\n```\n\n#### Linux (Snap): mounted drives are not visible in file selection dialog\n\nYou will also see following error if you run GridPlayer from terminal:\n\n```shell\nGLib-GIO-WARNING **: Error creating IO channel for /proc/self/mountinfo: Permission denied (g-file-error-quark, 2)\n```\n\nTo fix this, you need to allow GridPlayer snap to access system mount information and disk quotas via Snap Store or by running:\n\n```shell\n$ sudo snap connect gridplayer:mount-observe\n```\n\n#### Linux (KDE): black screen issue when using hardware decoder\n\nSwitch on "Opaque overlay (fix black screen)" checkbox in settings.\n\nOverlay might be a bit glitchy in KDE with hardware decoder.\n\n#### MacOS: "GridPlayer" is damaged and can\'t be opened\n\nTo fix this, you need to execute the following command using terminal:\n\n```shell\n$ sudo xattr -rd com.apple.quarantine /Applications/GridPlayer.app\n```\n\n## Attributions\n\nThis software was build using\n\n- **Python** by [Python Software Foundation](https://www.python.org/)\n  - Licensed under *Python Software Foundation License*\n- **Qt** by [Qt Project](https://www.qt.io/)\n  - Licensed under *GPL 2.0, GPL 3.0, and LGPL 3.0*\n- **VLC** by [VideoLAN](https://www.videolan.org/)\n  - Licensed under *GPL 2.0 or later*\n\n### Python packages\n\n- **PyQt** by [Riverbank Computing](https://riverbankcomputing.com/)\n  - Licensed under *Riverbank Commercial License and GPL v3*\n- **python-vlc** by [Olivier Aubert](https://github.com/oaubert/python-vlc)\n  - Licensed under *GPL 2.0 and LGPL 2.1*\n- **pydantic** by [Samuel Colvin](https://github.com/samuelcolvin/pydantic)\n  - Licensed under *MIT License*\n\n### Graphics\n\n- **Hack Font** by [Source Foundry](http://sourcefoundry.org/hack/)\n  - Licensed under *MIT License*\n- **Basic Icons** by [Icongeek26](https://www.flaticon.com/authors/icongeek26)\n  - Licensed under *Flaticon License*\n- **Suru Icons** by [Sam Hewitt](https://snwh.org/)\n  - Licensed under *Creative Commons Attribution-Share Alike 4.0*\n- **Clean App Download Buttons** by [Tony Thomas](https://medialoot.com/item/clean-app-download-buttons/)\n  - Licensed under *MediaLoot License*\n\n## License\n\nThis software is licensed under the terms of the GNU General Public License version 3 (GPLv3). Full text of the license is available in the [LICENSE](https://github.com/vzhd1701/gridplayer/blob/master/LICENSE) file and [online](https://www.gnu.org/licenses/gpl-3.0.html).\n',
    'author': 'vzhd1701',
    'author_email': 'vzhd1701@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vzhd1701/gridplayer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
