# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ranger_tmux']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.8.0,<6.0.0', 'ranger-fm>=1.9.3,<2.0.0']

entry_points = \
{'ranger.plugins': ['ranger_tmux = ranger_tmux.plugin']}

setup_kwargs = {
    'name': 'ranger-tmux',
    'version': '1.0.1',
    'description': 'Tmux integration for ranger',
    'long_description': '# ranger_tmux\n\nTmux integration for ranger\n\n## Install\n\nTo install this plugin, clone the respository into ranger\'s plugins folder:\n\n```\npip install git+https://github.com/joouha/ranger_tmux\npython -m ranger_tmux install\n```\n\n## Features\n\n<img src="https://i.postimg.cc/SRz46CNH/output.gif" align="right" width=300>\n\n- Open files from ranger in a new tmux window or pane\n- Make your terminal track ranger\'s directory\n- Make ranger track your terminal\'s directory\n- Set tmux window title to show ranger is running\n- Drop down file-manager in your tmux session\n- Easily split a ranger pane to launch a shell in the current folder\n\n### Other pane tracking & syncing\n\nThis plugin enables syncing of the current working directory between ranger and other tmux panes in the same window.\n\nThe pane to be used for syncing or tracking is determined in the following order:\n\n1. A marked pane;\n2. The currently selected pane;\n3. The last selected pane;\n4. The next pane.\n\nRanger will only sync its working directory to another pane if the process running in another pane does not have any child processes. This prevents ranger typing `cd` commands if you have launched a text editor from the shell in the other pane.\n\n### Drop-down ranger\n\nWhen installing the plugin, you will be asked if you want to install a key-binding in `~/.tmux.conf` for drop-down ranger. This allows you to toggle ranger in a drop-down tmux pane in the current window. This can be run manually by running `python -m ranger_tmux.drop` in a tmux session.\n\nThe key binding can be installed by running `python -m ranger_tmux --tmux install`, or by running the `:install_tmux_dropdown_shortcut` command in ranger (or typing the `xh` shortcut). The default key-binding installed is `prefix, backspace`, but this can be changed by editing the lines added to `~/.tmux.conf`.\n\n## Shortcut keys\n\n| Key Sequence | Command                                                                           |\n| ------------ | --------------------------------------------------------------------------------- |\n| `xc`         | Change the current working directory in the other pane to the directory in ranger |\n| `xd`         | Change ranger\'s current directory to the directory of the other pane              |\n| `xs`         | Toggle syncing of ranger\'s current directory to the other pane                    |\n| `xt`         | Toggle tracking of the other pane\'s working directory to tmux                     |\n| `xw`         | Toggle opening files in a new tmux window                                         |\n| `xi`         | Toggle setting the tmux window\'s title to "ranger" when ranger is running         |\n| `xe`         | Open the selected file with rifle in a new tmux window                            |\n| `x\\|`        | Split ranger\'s current tmux pane vertially                                        |\n| `x-`         | Split ranger\'s current tmux pane horizontally                                     |\n| `xh`         | Adds the dropdown shortcut to `~/.tmux.conf`                                      |\n\n## Settings\n\nThis plugin adds several settings to ranger:\n\n| Setting                   | Type  | Default | Meaning                                                                                  |\n| ------------------------- | ----- | ------- | ---------------------------------------------------------------------------------------- |\n| `tmux_cwd_sync`           | bool  | False   | When True, ranger\'s current directory is synced to the other pane                        |\n| `tmux_cwd_track`          | bool  | False   | When True, ranger\'s current directory tracks the other pane                              |\n| `tmux_cwd_track_interval` | float | 0.5     | Time between checks of the directory of the other pane when tracking                     |\n| `tmux_open_in_window`     | bool  | True    | When True, files opened with ranger will open in a new tmux window                       |\n| `tmux_set_title`          | bool  | True    | When True, the tumx window will be renamed to "ranger" when ranger is running            |\n| `tmux_dropdown_percent`   | int   | 60      | The height of the pane created when the drop-down tmux key-binding is installed and used |\n| `tmux_dropdown_animate`   | bool  | True    | When True, dropped-down ranger will grow / shrink when summoned                          |\n| `tmux_dropdown_duration`  | float | 100     | Drop-down animation time in miliseconds                                                  |\n\nThe default values can be modified by setting them in `~/.config/ranger/rc.conf`, e.g.:\n\n```\nset tmux_cwd_sync true\nset tmux_cwd_track true\nset tmux_set_title true\nset tmux_open_in_window true\nset tmux_dropdown_percent 60\n```\n',
    'author': 'Josiah Outram Halstead',
    'author_email': 'josiah@halstead.email',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/joouha/ranger_tmux',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
