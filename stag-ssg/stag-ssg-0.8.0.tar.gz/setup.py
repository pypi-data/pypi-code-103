# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['stag',
 'stag.plugins',
 'stag.plugins.adoc',
 'stag.plugins.macros',
 'stag.plugins.md',
 'stag.plugins.taxonomies',
 'stag.plugins.xml',
 'stag.writers']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21,<22',
 'jinja2>=3,<4',
 'markdown>=3,<4',
 'python-dateutil>=2.8.0,<3.0.0',
 'python-slugify>=5,<6',
 'tomli>=1.2,<2.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.0,<5.0']}

entry_points = \
{'console_scripts': ['stag = stag.stag:main']}

setup_kwargs = {
    'name': 'stag-ssg',
    'version': '0.8.0',
    'description': 'Deadly simple static site generator',
    'long_description': '<p align="center">\n  <a href="https://git.goral.net.pl/mgoral/stag">\n    <img alt="Logo featuring a stag" src="https://git.goral.net.pl/mgoral/stag/raw/branch/master/doc/stag.png" width="320"/>\n  </a>\n</p>\n\n# Stag\n\nStag is a simple, extensible static site generator, where almost every part\nis a plug in. It\'s almost too easy to extend it with your own\nfunctionalities.\n\n# Features\n\nOut of the box Stag comes with the following features:\n\n- pages can be generated from Markdown with enabled support for footnotes,\n  fenced code blocks and some typographic goodies.\n- support for Asciidoc (via asciidoctor)\n- generic support for file front matters\n- Jinja2 templates\n- taxonomies (e.g. tags)\n- RSS feeds\n- generation of nice URLs:\n  - _foo/index.md_ → _foo/index.html_\n  - _bar.md_ → _bar/index.html_\n- extensible with plugins and macros (shortcodes)\n\n# Installation\n\nPyPI: https://pypi.org/project/stag-ssg/\n',
    'author': 'Michal Goral',
    'author_email': 'dev@goral.net.pl',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://git.goral.net.pl/mgoral/stag',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
