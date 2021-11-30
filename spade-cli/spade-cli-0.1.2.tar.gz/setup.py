# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spade', 'spade.commands']

package_data = \
{'': ['*']}

install_requires = \
['dnspython>=2.1,<3.0',
 'pydantic>=1.8,<2.0',
 'rich>=10.14,<11.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['spade = spade.cli:spade']}

setup_kwargs = {
    'name': 'spade-cli',
    'version': '0.1.2',
    'description': "You can't dig without a spade! - a super-powered networking tool!",
    'long_description': "# Spade CLI\n`spade` is the next-generation networking command line tool.\nSay goodbye to the likes of dig, ping and traceroute with more accessible,\nmore informative and prettier output.\n\n![image](https://user-images.githubusercontent.com/44979306/143790954-c058f58b-0941-4b2d-b3ff-057916cf487f.png)\n\nSpade is fully operational on all major operating systems, this includes Windows, Linux and MacOS.\n\n## Documentation\nFor an introduction into the capabilities Spade CLI offers we recommend you try\nrunning `spade --help` in your terminal and giving it a read. For further\ninformation, check out [the manual](https://example.com/).\n\n## Contributing\nIf something isn't quite right, or something could be even better, we'd love for you to let us know.\nThen, either you or somebody else from our community can try and fix it. If you'd like to get started\nwith developing Spade CLI check out our [contributing guide](https://github.com/doublevcodes/spade/blob/main/CONTRIBUTING.md).\n",
    'author': 'Vivaan Verma',
    'author_email': 'hello@vivaanverma.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
