# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wordlists']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'wordlists',
    'version': '1.0.0',
    'description': 'Utilities to download word lists in Python',
    'long_description': '# wordlists\n\nUtilities to download word lists in Python.\n\n## Usage\n\n```py\nfrom wordlists import update_lists, read_words\n\n\n# Update the word lists from the web\nupdate_lists()\n\n# Get the words from a list\nwords = read_words("dwyl_alpha")\n\n# Filter words which are 27 characters\nwords = [w for w in words if len(w) == 27]\n\n# Print the words\nprint(words)  # [\'electroencephalographically\', \'hydroxydesoxycorticosterone\', \'microspectrophotometrically\']\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/wordlists',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
