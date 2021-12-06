# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pick']

package_data = \
{'': ['*']}

extras_require = \
{':sys_platform == "win32"': ['windows-curses>=2.2.0,<3.0.0']}

setup_kwargs = {
    'name': 'pick',
    'version': '1.1.1',
    'description': 'Pick an option in the terminal with a simple GUI',
    'long_description': "pick\n====\n\n.. image:: https://circleci.com/gh/wong2/pick/tree/master.svg?style=svg\n   :target: https://circleci.com/gh/wong2/pick/tree/master\n\n.. image:: https://img.shields.io/pypi/v/pick.svg\n   :alt: PyPI\n   :target: https://pypi.python.org/pypi/pick\n\n**pick** is a small python library to help you create curses based interactive selection list in the terminal. See it in action:\n\n.. image:: https://github.com/wong2/pick/raw/master/example/basic.gif\n   :alt: Demo\n\nInstallation\n------------\n\n::\n\n    $ pip install pick\n\nUsage\n-----\n\n**pick** comes with a simple api::\n\n    >>> from pick import pick\n\n    >>> title = 'Please choose your favorite programming language: '\n    >>> options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']\n    >>> option, index = pick(options, title)\n    >>> print(option)\n    >>> print(index)\n\n**outputs**::\n\n    >>> C++\n    >>> 4\n\n**pick** multiselect example::\n\n    >>> from pick import pick\n\n    >>> title = 'Please choose your favorite programming language (press SPACE to mark, ENTER to continue): '\n    >>> options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']\n    >>> selected = pick(options, title, multiselect=True, min_selection_count=1)\n    >>> print(selected)\n\n**outputs**::\n\n    >>> [('Java', 0), ('C++', 4)]\n\n\nOptions\n-------\n\n* ``options``: a list of options to choose from\n* ``title``: (optional) a title above options list\n* ``indicator``: (optional) custom the selection indicator, defaults to *\n* ``default_index``: (optional) set this if the default selected option is not the first one\n* ``multiselect``: (optional), if set to True its possible to select multiple items by hitting SPACE\n* ``min_selection_count``: (optional) for multi select feature to dictate a minimum of selected items before continuing\n* ``options_map_func``: (optional) a mapping function to pass each option through before displaying\n\nRegister custom handlers\n------------------------\n\nSometimes you may need to register custom handlers for specific keyboard keys, you can use the ``register_custom_handler`` API::\n\n    >>> from pick import Picker\n    >>> title, options = 'Title', ['Option1', 'Option2']\n    >>> picker = Picker(options, title)\n    >>> def go_back(picker):\n    ...     return None, -1\n    >>> picker.register_custom_handler(ord('h'),  go_back)\n    >>> option, index = picker.start()\n\n* the custom handler will be called with the ``picker`` instance as it's parameter.\n* the custom handler should either return a two element tuple, or None.\n* if None is returned, the picker would continue to run, otherwise the picker will stop and return the tuple.\n\nOptions Map Function\n--------------------\n\nIf your options are not in a format that you want displayed (such as a dictionary), you can pass in a mapping function which each option will be run through. The return value of the function will be displayed.\n\n* the selected option returned will be the original value and not the displayed return result from the ``options_map_func`` function.\n\n**pick** options map function example::\n\n    >>> from pick import pick\n\n    >>> title = 'Please choose an option: '\n    >>> options = [{'label': 'option1'}, {'label': 'option2'}, {'label': 'option3'}]\n\n    >>> def get_label(option): return option.get('label')\n\n    >>> selected = pick(options, title, indicator='*', options_map_func=get_label)\n    >>> print(selected)\n\n**displays**::\n\n    Please choose an option:\n\n    * option1\n      option2\n      option3\n\n**outputs**::\n\n    >>> ({ 'label': 'option1' }, 0)\n",
    'author': 'wong2',
    'author_email': 'wonderfuly@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wong2/pick',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
