# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manim',
 'manim._config',
 'manim.animation',
 'manim.camera',
 'manim.cli',
 'manim.cli.cfg',
 'manim.cli.init',
 'manim.cli.new',
 'manim.cli.plugins',
 'manim.cli.render',
 'manim.grpc',
 'manim.grpc.gen',
 'manim.grpc.impl',
 'manim.gui',
 'manim.mobject',
 'manim.mobject.svg',
 'manim.mobject.types',
 'manim.opengl',
 'manim.plugins',
 'manim.renderer',
 'manim.scene',
 'manim.utils',
 'manim.utils.docbuild',
 'manim.utils.testing']

package_data = \
{'': ['*'],
 'manim': ['templates/*'],
 'manim.grpc': ['proto/*'],
 'manim.renderer': ['shaders/*',
                    'shaders/default/*',
                    'shaders/image/*',
                    'shaders/include/*',
                    'shaders/manim_coords/*',
                    'shaders/quadratic_bezier_fill/*',
                    'shaders/quadratic_bezier_stroke/*',
                    'shaders/surface/*',
                    'shaders/test/*',
                    'shaders/textured_surface/*',
                    'shaders/true_dot/*',
                    'shaders/vectorized_mobject_fill/*',
                    'shaders/vectorized_mobject_stroke/*',
                    'shaders/vertex_colors/*']}

install_requires = \
['Pillow',
 'click-default-group',
 'click>=7.1',
 'cloup>=0.7.0,<0.8.0',
 'colour',
 'decorator>=5.0.7,<6.0.0',
 'isosurfaces==0.1.0',
 'manimpango>=0.3.0,<0.4.0',
 'mapbox-earcut>=0.12.10,<0.13.0',
 'moderngl-window>=2.3.0,<3.0.0',
 'moderngl>=5.6.3,<6.0.0',
 'networkx>=2.5,<3.0',
 'numpy>=1.9,<2.0',
 'pycairo>=1.19,<2.0',
 'pydub',
 'pygments',
 'requests',
 'rich>=6.0',
 'scipy',
 'screeninfo>=0.6.7,<0.7.0',
 'setuptools',
 'skia-pathops>=0.7.0,<0.8.0',
 'srt>=3.5.0,<4.0.0',
 'tqdm',
 'watchdog']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 'gui': ['dearpygui>=0.8,<0.9'],
 'jupyterlab': ['jupyterlab>=3.0,<4.0'],
 'webgl_renderer': ['grpcio>=1.33.0,<1.34.0', 'grpcio-tools>=1.33.0,<1.34.0']}

entry_points = \
{'console_scripts': ['manim = manim.__main__:main',
                     'manimce = manim.__main__:main']}

setup_kwargs = {
    'name': 'manim',
    'version': '0.13.0',
    'description': 'Animation engine for explanatory math videos.',
    'long_description': '<p align="center">\n    <a href="https://www.manim.community/"><img src="https://raw.githubusercontent.com/ManimCommunity/manim/main/logo/cropped.png"></a>\n    <br />\n    <br />\n    <a href="https://pypi.org/project/manim/"><img src="https://img.shields.io/pypi/v/manim.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>\n    <a href="https://hub.docker.com/r/manimcommunity/manim"><img src="https://img.shields.io/docker/v/manimcommunity/manim?color=%23099cec&label=docker%20image&logo=docker" alt="Docker image"> </a>\n    <a href="https://mybinder.org/v2/gh/ManimCommunity/jupyter_examples/HEAD?filepath=basic_example_scenes.ipynb"><img src="https://mybinder.org/badge_logo.svg"></a>\n    <a href="http://choosealicense.com/licenses/mit/"><img src="https://img.shields.io/badge/license-MIT-red.svg?style=flat" alt="MIT License"></a>\n    <a href="https://www.reddit.com/r/manim/"><img src="https://img.shields.io/reddit/subreddit-subscribers/manim.svg?color=orange&label=reddit&logo=reddit" alt="Reddit" href=></a>\n    <a href="https://twitter.com/manim_community/"><img src="https://img.shields.io/twitter/url/https/twitter.com/cloudposse.svg?style=social&label=Follow%20%40manim_community" alt="Twitter">\n    <a href="https://www.manim.community/discord/"><img src="https://img.shields.io/discord/581738731934056449.svg?label=discord&color=yellow&logo=discord" alt="Discord"></a>\n    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">\n    <a href="https://docs.manim.community/"><img src="https://readthedocs.org/projects/manimce/badge/?version=latest" alt="Documentation Status"></a>\n    <a href="https://pepy.tech/project/manim"><img src="https://pepy.tech/badge/manim/month?" alt="Downloads"> </a>\n    <img src="https://github.com/ManimCommunity/manim/workflows/CI/badge.svg" alt="CI">\n    <br />\n    <br />\n    <i>An animation engine for explanatory math videos</i>\n</p>\n<hr />\n\nManim is an animation engine for explanatory math videos. It\'s used to create precise animations programmatically, as demonstrated in the videos of [3Blue1Brown](https://www.3blue1brown.com/).\n\n> NOTE: This repository is maintained by the Manim Community and is not associated with Grant Sanderson or 3Blue1Brown in any way (although we are definitely indebted to him for providing his work to the world). If you would like to study how Grant makes his videos, head over to his repository ([3b1b/manim](https://github.com/3b1b/manim)). This fork is updated more frequently than his, and it\'s recommended to use this fork if you\'d like to use Manim for your own projects.\n\n## Table of Contents:\n\n-  [Installation](#installation)\n-  [Usage](#usage)\n-  [Documentation](#documentation)\n-  [Docker](#docker)\n-  [Help with Manim](#help-with-manim)\n-  [Contributing](#contributing)\n-  [License](#license)\n\n## Installation\n\n> **WARNING:** These instructions are for the community version _only_. Trying to use these instructions to install [3b1b/manim](https://github.com/3b1b/manim) or instructions there to install this version will cause problems. Read [this](https://docs.manim.community/en/stable/installation/versions.html) and decide which version you wish to install, then only follow the instructions for your desired version.\n\nManim requires a few dependencies that must be installed prior to using it. If you\nwant to try it out first before installing it locally, you can do so\n[in our online Jupyter environment](https://try.manim.community/).\n\nFor local installation, please visit the [Documentation](https://docs.manim.community/en/stable/installation.html)\nand follow the appropriate instructions for your operating system.\n\n## Usage\n\nManim is an extremely versatile package. The following is an example `Scene` you can construct:\n\n```python\nfrom manim import *\n\n\nclass SquareToCircle(Scene):\n    def construct(self):\n        circle = Circle()\n        square = Square()\n        square.flip(RIGHT)\n        square.rotate(-3 * TAU / 8)\n        circle.set_fill(PINK, opacity=0.5)\n\n        self.play(Create(square))\n        self.play(Transform(square, circle))\n        self.play(FadeOut(square))\n```\n\nIn order to view the output of this scene, save the code in a file called `example.py`. Then, run the following in a terminal window:\n\n```sh\nmanim -p -ql example.py SquareToCircle\n```\n\nYou should see your native video player program pop up and play a simple scene in which a square is transformed into a circle. You may find some more simple examples within this\n[GitHub repository](example_scenes). You can also visit the [official gallery](https://docs.manim.community/en/stable/examples.html) for more advanced examples.\n\nManim also ships with a `%%manim` IPython magic which allows to use it conveniently in JupyterLab (as well as classic Jupyter) notebooks. See the\n[corresponding documentation](https://docs.manim.community/en/stable/reference/manim.utils.ipython_magic.ManimMagic.html) for some guidance and\n[try it out online](https://mybinder.org/v2/gh/ManimCommunity/jupyter_examples/HEAD?filepath=basic_example_scenes.ipynb).\n\n## Command line arguments\n\nThe general usage of Manim is as follows:\n\n![manim-illustration](https://raw.githubusercontent.com/ManimCommunity/manim/main/docs/source/_static/command.png)\n\nThe `-p` flag in the command above is for previewing, meaning the video file will automatically open when it is done rendering. The `-ql` flag is for a faster rendering at a lower quality.\n\nSome other useful flags include:\n\n-  `-s` to skip to the end and just show the final frame.\n-  `-n <number>` to skip ahead to the `n`\'th animation of a scene.\n-  `-f` show the file in the file browser.\n\nFor a thorough list of command line arguments, visit the [documentation](https://docs.manim.community/en/stable/tutorials/configuration.html).\n\n## Documentation\n\nDocumentation is in progress at [ReadTheDocs](https://docs.manim.community/).\n\n## Docker\n\nThe community also maintains a docker image (`manimcommunity/manim`), which can be found [on DockerHub](https://hub.docker.com/r/manimcommunity/manim). The following tags are supported:\n\n- `latest` -- the most recent version corresponding to [the main branch](https://github.com/ManimCommunity/manim)\n- `stable` -- the latest released version (according to [the releases page](https://github.com/ManimCommunity/manim/releases))\n- `vX.Y.Z` -- any particular released version (according to [the releases page](https://github.com/ManimCommunity/manim/releases))\n\n### Instructions for running the docker image\n\n#### Quick Example\nTo render a scene `CircleToSquare` in a file `test_scenes.py` contained in your current working directory while preserving your user and group ID, use\n\n```sh\ndocker run --rm -it  --user="$(id -u):$(id -g)" -v "$(pwd)":/manim manimcommunity/manim manim test_scenes.py CircleToSquare -qm\n```\n\n#### Running the image in the background\n\nInstead of using the "throwaway container" approach sketched above, you can also create a named container that you can also modify to your liking. First, run\n\n```sh\ndocker run -it --name my-manim-container -v "$(pwd):/manim" manimcommunity/manim /bin/bash\n```\n\nto obtain an interactive shell inside your container allowing you to, e.g., install further dependencies (like texlive packages using `tlmgr`). Exit the container as soon as you are satisfied. Then, before using it, start the container by running\n\n```sh\ndocker start my-manim-container\n```\n\nThen, to render a scene `CircleToSquare` in a file `test_scenes.py`, call\n\n```sh\ndocker exec -it --user="$(id -u):$(id -g)" my-manim-container manim test.py CircleToSquare -qm\n```\n\n#### Jupyterlab\n\nAnother alternative is to use the docker image to spin up a local webserver running\nJupyterLab in whose Python kernel manim is installed and can be accessed via the `%%manim` cell magic.\nTo use JupyterLab, run\n\n```sh\ndocker run -it -p 8888:8888 manimcommunity/manim jupyter lab --ip=0.0.0.0\n```\n\nand then follow the instructions in the terminal.\n\n#### Important notes\n\nWhen executing `manim` within a Docker container, several command line flags (in particular `-p` (preview file) and `-f` (show output file in the file browser)) are not supported.\n\n## Help with Manim\n\nIf you need help installing or using Manim, feel free to reach out to our [Discord\nServer](https://www.manim.community/discord/) or [Reddit Community](https://www.reddit.com/r/manim). If you would like to submit a bug report or feature request, please open an issue.\n\n## Contributing\n\nContributions to Manim are always welcome. In particular, there is a dire need for tests and documentation. For contribution guidelines, please see the [documentation](https://docs.manim.community/en/stable/contributing.html).\n\nMost developers on the project use `poetry` for management. You\'ll want to have poetry installed and available in your environment.\nLearn more about `poetry` at its [documentation](https://python-poetry.org/docs/) and find out how to install manim with poetry at the [manim dev-installation guide](https://docs.manim.community/en/stable/contributing/development.html) in the manim documentation.\n\n## How to Cite Manim\n\nWe acknowledge the importance of good software to support research, and we note\nthat research becomes more valuable when it is communicated effectively. To\ndemonstrate the value of Manim, we ask that you cite Manim in your work.\nCurrently, the best way to cite Manim is to go to our\n[repository page](https://github.com/ManimCommunity/manim) (if you aren\'t already) and\nclick the "cite this repository" button on the right sidebar. This will generate\na citation in your preferred format, and will also integrate well with citation managers.\n\n## Code of Conduct\n\nOur full code of conduct, and how we enforce it, can be read on [our website](https://docs.manim.community/en/stable/conduct.html).\n\n## License\n\nThe software is double-licensed under the MIT license, with copyright by 3blue1brown LLC (see LICENSE), and copyright by Manim Community Developers (see LICENSE.community).\n',
    'author': 'The Manim Community Developers',
    'author_email': 'contact@manim.community',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.manim.community/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
