# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vcspull']

package_data = \
{'': ['*']}

install_requires = \
['click>=7', 'colorama>=0.3.9', 'kaptan', 'libvcs>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['vcspull = vcspull:cli.cli']}

setup_kwargs = {
    'name': 'vcspull',
    'version': '1.8.1',
    'description': 'synchronize your projects via yaml / json files',
    'long_description': '`vcspull` - synchronize your repos. built on\n[libvcs](https://github.com/vcs-python/libvcs)\n\n[![Python Package](https://img.shields.io/pypi/v/vcspull.svg)](http://badge.fury.io/py/vcspull)\n[![Docs](https://github.com/vcs-python/vcspull/workflows/Publish%20Docs/badge.svg)](https://github.com/vcs-python/vcspull/actions?query=workflow%3A%22Publish+Docs%22)\n[![Build Status](https://github.com/vcs-python/vcspull/workflows/tests/badge.svg)](https://github.com/vcs-python/vcspull/actions?query=workflow%3A%22tests%22)\n[![Code Coverage](https://codecov.io/gh/vcs-python/vcspull/branch/master/graph/badge.svg)](https://codecov.io/gh/vcs-python/vcspull)\n![License](https://img.shields.io/github/license/vcs-python/vcspull.svg)\n\nManage your commonly used repos from YAML / JSON manifest(s). Compare to\n[myrepos](http://myrepos.branchable.com/).\n\nGreat if you use the same repos at the same locations across multiple\nmachines or want to clone / update a pattern of repos without having to\n`cd` into each one.\n\n- clone /update to the latest repos with `$ vcspull`\n- use filters to specify a location, repo url or pattern in the\n  manifest to clone / update\n- supports svn, git, hg version control systems\n- automatically checkout fresh repositories\n- [Documentation](https://vcspull.git-pull.com/) and\n  [Examples](https://vcspull.git-pull.com/examples.html).\n- supports [pip](http://www.pip-installer.org/)-style URL\'s\n  ([RFC3986](http://tools.ietf.org/html/rfc3986.html)-based [url\n  scheme](http://www.pip-installer.org/logic.html#vcs-support))\n\n# how to\n\n## install\n\n```sh\n$ pip install --user vcspull\n```\n\n## configure\n\nadd repos you want vcspull to manage to `~/.vcspull.yaml`.\n\n_vcspull does not currently scan for repos on your system, but it may in\nthe future_\n\n```yaml\n~/code/:\n  flask: "git+https://github.com/mitsuhiko/flask.git"\n~/study/c:\n  awesome: "git+git://git.naquadah.org/awesome.git"\n~/study/data-structures-algorithms/c:\n  libds: "git+https://github.com/zhemao/libds.git"\n  algoxy:\n    repo: "git+https://github.com/liuxinyu95/AlgoXY.git"\n    remotes:\n      tony: "git+ssh://git@github.com/tony/AlgoXY.git"\n```\n\n(see the author\'s\n[.vcspull.yaml](https://github.com/tony/.dot-config/blob/master/.vcspull.yaml),\nmore [examples](https://vcspull.git-pull.com/examples.html).)\n\nnext, on other machines, copy your `$HOME/.vcspull.yaml` file or\n`$HOME/.vcspull/` directory them and you can clone your repos\nconsistently. vcspull automatically handles building nested directories.\nUpdating already cloned/checked out repos is done automatically if they\nalready exist.\n\n## clone / update your repos\n\n```bash\n$ vcspull\n```\n\nkeep nested VCS repositories updated too, lets say you have a mercurial\nor svn project with a git dependency:\n\n`external_deps.yaml` in your project root, (can be anything):\n\n```yaml\n./vendor/:\n  sdl2pp: "git+https://github.com/libSDL2pp/libSDL2pp.git"\n```\n\nclone / update repos:\n\n    $ vcspull -c external_deps.yaml\n\nSee the [Quickstart](https://vcspull.git-pull.com/quickstart.html) for\nmore.\n\n## pulling specific repos\n\nhave a lot of repos?\n\nyou can choose to update only select repos through\n[fnmatch](http://pubs.opengroup.org/onlinepubs/009695399/functions/fnmatch.html)\npatterns. remember to add the repos to your `~/.vcspull.{json,yaml}`\nfirst.\n\nThe patterns can be filtered by by directory, repo name or vcs url.\n\n```bash\n# any repo starting with "fla"\n$ vcspull "fla*"\n# any repo with django in the name\n$ vcspull "*django*"\n\n# search by vcs + url\n# since urls are in this format <vcs>+<protocol>://<url>\n$ vcspull "git+*"\n\n# any git repo with python in the vcspull\n$ vcspull "git+*python*\n\n# any git repo with django in the vcs url\n$ vcspull "git+*django*"\n\n# all repositories in your ~/code directory\n$ vcspull "$HOME/code/*"\n```\n\n<img src="https://raw.githubusercontent.com/vcs-python/vcspull/master/docs/_static/vcspull-demo.gif" class="align-center" style="width:45.0%" alt="image" />\n\n# Donations\n\nYour donations fund development of new features, testing and support.\nYour money will go directly to maintenance and development of the\nproject. If you are an individual, feel free to give whatever feels\nright for the value you get out of the project.\n\nSee donation options at <https://git-pull.com/support.html>.\n\n# More information\n\n- Python support: >= 3.6, pypy\n- VCS supported: git(1), svn(1), hg(1)\n- Source: <https://github.com/vcs-python/vcspull>\n- Docs: <https://vcspull.git-pull.com>\n- Changelog: <https://vcspull.git-pull.com/history.html>\n- API: <https://vcspull.git-pull.com/api.html>\n- Issues: <https://github.com/vcs-python/vcspull/issues>\n- Test Coverage: <https://codecov.io/gh/vcs-python/vcspull>\n- pypi: <https://pypi.python.org/pypi/vcspull>\n- Open Hub: <https://www.openhub.net/p/vcspull>\n- License: [MIT](https://opensource.org/licenses/MIT).\n',
    'author': 'Tony Narlock',
    'author_email': 'tony@git-pull.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://vcspull.git-pull.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
