# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakypy',
 'snakypy.zshpower',
 'snakypy.zshpower.commands',
 'snakypy.zshpower.commands.utils',
 'snakypy.zshpower.config',
 'snakypy.zshpower.database',
 'snakypy.zshpower.prompt',
 'snakypy.zshpower.prompt.sections',
 'snakypy.zshpower.prompt.sections.utils',
 'snakypy.zshpower.utils']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'snakypy-helpers>=0.2.2,<0.3.0',
 'tomlkit>=0.7.1,<0.8.0']

entry_points = \
{'console_scripts': ['zshpower = snakypy.zshpower.cli:main',
                     'zshpower-draw = snakypy.zshpower.draw:main']}

setup_kwargs = {
    'name': 'zshpower',
    'version': '0.11.3',
    'description': 'ZSHPower is a theme for ZSH with a manager.',
    'long_description': '.. image:: https://raw.githubusercontent.com/snakypy/assets/master/zshpower/images/zshpower-transparent.png\n    :align: center\n    :alt: ZSHPower\n\n_________________\n\n.. image:: https://github.com/snakypy/zshpower/workflows/Tests/badge.svg\n    :target: https://github.com/snakypy/zshpower\n\n.. image:: https://img.shields.io/pypi/v/zshpower.svg\n    :target: https://pypi.python.org/pypi/zshpower\n    :alt: PyPI - ZSHPower\n\n.. image:: https://img.shields.io/pypi/wheel/zshpower\n    :target: https://pypi.org/project/wheel/\n    :alt: PyPI - Wheel\n\n.. image:: https://img.shields.io/pypi/pyversions/zshpower\n    :target: https://pyup.io/repos/github/snakypy/zshpower/\n    :alt: Python versions\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: Black\n\n.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336\n    :target: https://pycqa.github.io/isort/\n    :alt: Isort\n\n.. image:: http://www.mypy-lang.org/static/mypy_badge.svg\n    :target: http://mypy-lang.org/\n    :alt: Mypy\n\n.. image:: https://pyup.io/repos/github/snakypy/zshpower/shield.svg\n   :target: https://pyup.io/repos/github/snakypy/zshpower/\n   :alt: Updates\n\n.. image:: https://img.shields.io/github/issues-raw/snakypy/zshpower\n    :target: https://github.com/snakypy/zshpower/issues\n    :alt: GitHub issues\n\n.. image:: https://img.shields.io/github/license/snakypy/zshpower\n    :target: https://github.com/snakypy/zshpower/blob/master/LICENSE\n    :alt: GitHub license\n\n_________________\n\n`ZSHPower` is a theme for ZSH; especially for the `Python`_ developer. Pleasant to look at, the **ZSHPower** comforts you with its colors and icons vibrant.\n\nInstalling **ZSHPower** is the easiest thing you will see in any existing theme for **ZSH**, because there is a manager.\n\nThe changes in the theme become more dynamic through a configuration file, where the user can make various combinations for the style of **ZSHPower**.\n\nThe **ZSHPower** supports installation along with `Oh My ZSH`_, where changes to: **enable** and **disable** an `Oh My ZSH`_ theme are easier, all in a simplified command line, without opening any files or creating symbolic links.\n\nIn addition, the **ZSHPower** manager downloads **Oh My Zsh** and the\n`zsh-autosuggestions`_ and `zsh-syntax-highlighting`_ plugins automatically, everything to make your ZSH very power.\n\n\nRequirements\n------------\n\nTo work correctly, you will first need:\n\n* `git`_ (v2.25 or recent) must be installed.\n* `zsh`_  (v5.2 or recent) must be installed.\n* `python`_ (v3.9 or recent) must be installed.\n* `sqlite3`_ (v3.35 or recent) must be installed.\n* `pip`_ (v21.0.1 or recent) must be installed.\n* `nerd fonts`_ must be installed.\n\n\nFeatures\n--------\n\n* `Oh My Zsh`_ installation automatically;*\n* Automatically install `zsh-autosuggestions`_ and `zsh-syntax-highlighting`_;\n* Automated installation and uninstallation;\n* Enable and disable `ZSHPower` anytime;\n* Upgrade `ZSHPower` effortlessly;\n* Reset the settings with one command only;\n* Personalized directory with truncate option;\n* Current Git branch and rich repo status:\n    *  — untracked changes;\n    *  — new files added;\n    *  — deleted files;\n    *  — new modified files;\n    *  — commits made;\n    *  — and more.\n* Application versions shown with `nerd fonts`_, they are:\n    * CMake, Crystal, Dart, Deno, Docker, Docker, Dotnet, Elixir, Erlang, Go, Gulp, Helm, Java, Julia, Kotlin, Nim, NodeJS, Ocaml, Perl, Php, Python, Ruby, Rust, Scala, Vagrant, Zig\n* Package versions such as Crystal, Helm, NodeJS, Python, Rust shown;\n* Shows the time in the upper right corner;\n* and, many other dynamic settings in `$HOME/.zshpower/config/zshpower.toml`.\n\n\\* features if used with **Oh My ZSH**.\n\n\nInstalling\n----------\n\nGlobally:\n\n.. code-block:: shell\n\n    $ sudo python -m pip install zshpower\n\nNOTE: It is not recommended to install globally.\n\nFor the user:\n\n.. code-block:: shell\n\n    $ python -m pip install zshpower --user\n\n\nUsing\n-----\n\nRun the command below to set `ZSHPower`_ on your ZSH:\n\n.. code-block:: shell\n\n    $ zshpower init\n\nIf you want to use ZSHPower with `Oh My Zsh`_, use the **--omz** flag:\n\n.. code-block:: shell\n\n    $ zshpower init --omz\n\nFor more command information, run:\n\n.. code-block:: shell\n\n    $ zshpower --help\n\nMore information: https://github.com/snakypy/zshpower\n\nDonation\n--------\n\nClick on the image below to be redirected the donation forms:\n\n.. image:: https://raw.githubusercontent.com/snakypy/donations/master/svg/donate/donate-hand.svg\n    :width: 160 px\n    :height: 100px\n    :target: https://github.com/snakypy/donations/blob/master/README.md\n\n\nLicense\n-------\n\nThe gem is available as open source under the terms of the `MIT License`_ ©\n\nCredits\n-------\n\nSee, `AUTHORS`_.\n\nLinks\n-----\n\n* Code: https://github.com/snakypy/zshpower\n* Documentation: https://github.com/snakypy/zshpower/blob/master/README.md\n* Releases: https://pypi.org/project/zshpower/#history\n* Issue tracker: https://github.com/snakypy/zshpower/issues\n\n.. _AUTHORS: https://github.com/snakypy/zshpower/blob/master/AUTHORS.rst\n.. _Oh My Zsh: https://ohmyz.sh\n.. _zsh-autosuggestions: https://github.com/zsh-users/zsh-autosuggestions\n.. _zsh-syntax-highlighting: https://github.com/zsh-users/zsh-syntax-highlighting\n.. _ZSHPower: https://github.com/snakypy/zshpower\n.. _git: https://git-scm.com/downloads\n.. _zsh: http://www.zsh.org/\n.. _python: https://python.org\n.. _sqlite3: https://www.sqlite.org\n.. _pip: https://pip.pypa.io/en/stable/quickstart/\n.. _nerd fonts: https://www.nerdfonts.com/font-downloads\n.. _MIT License: https://github.com/snakypy/zshpower/blob/master/LICENSE\n.. _William Canin: http://williamcanin.github.io\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`williamcanin/pypkg-cookiecutter`: https://github.com/williamcanin/pypkg-cookiecutter\n',
    'author': 'William C. Canin',
    'author_email': 'william.costa.canin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/snakypy/zshpower',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
