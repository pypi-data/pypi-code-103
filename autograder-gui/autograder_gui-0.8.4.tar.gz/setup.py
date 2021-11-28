# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autograder_gui']

package_data = \
{'': ['*'],
 'autograder_gui': ['static/css/*',
                    'static/images/*',
                    'static/js/*',
                    'static/lib/codemirror/css/*',
                    'static/lib/codemirror/js/*',
                    'static/lib/codemirror/mode/*',
                    'static/lib/css/*',
                    'static/lib/fontawesome/*',
                    'static/lib/fontawesome/css/*',
                    'static/lib/fontawesome/js/*',
                    'static/lib/fontawesome/less/*',
                    'static/lib/fontawesome/metadata/*',
                    'static/lib/fontawesome/scss/*',
                    'static/lib/fontawesome/sprites/*',
                    'static/lib/fontawesome/svgs/brands/*',
                    'static/lib/fontawesome/svgs/regular/*',
                    'static/lib/fontawesome/svgs/solid/*',
                    'static/lib/fontawesome/webfonts/*',
                    'static/lib/fonts/*',
                    'static/lib/fonts/static/*',
                    'static/lib/js/*',
                    'static/templates/*']}

install_requires = \
['Eel[jinja2]>=0.14.0,<0.15.0',
 'assignment-autograder>=3.0.1,<4.0.0',
 'filetype>=1.0.8,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0']

entry_points = \
{'console_scripts': ['autograder_gui = autograder_gui.__main__:run']}

setup_kwargs = {
    'name': 'autograder-gui',
    'version': '0.8.4',
    'description': '',
    'long_description': None,
    'author': 'Ovsyanka',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ovsyanka83/autograder_electron',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
