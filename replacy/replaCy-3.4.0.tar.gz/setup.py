# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['replacy']

package_data = \
{'': ['*'], 'replacy': ['resources/*']}

install_requires = \
['jsonschema>=2.6.0,<3.0.0', 'lemminflect==0.2.1', 'pyfunctional>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'replacy',
    'version': '3.4.0',
    'description': 'ReplaCy = spaCy Matcher + pyInflect. Create rules, correct sentences.',
    'long_description': '<p align="center">\n<img src="./docs/replacy_logo.png" align="center" />\n</p>\n\n# replaCy: match & replace with spaCy\n\nWe found that in multiple projects we had duplicate code for using spaCy’s blazing fast matcher to do the same thing: Match-Replace-Grammaticalize. So we wrote replaCy!\n\n- Match - spaCy’s matcher is great, and lets you match on text, shape, POS, dependency parse, and other features. We extended this with “match hooks”, predicates that get used in the callback function to further refine a match.\n- Replace - Not built into spaCy’s matcher syntax, but easily added. You often want to replace a matched word with some other term.\n- Grammaticalize - If you match on ”LEMMA”: “dance”, and replace with suggestions: ["sing"], but the actual match is danced, you need to conjugate “sing” appropriately. This is the “killer feature” of replaCy\n\n[![spaCy](https://img.shields.io/badge/made%20with%20❤%20and-spaCy-09a3d5.svg)](https://spacy.io)\n[![pypi Version](https://img.shields.io/pypi/v/replacy.svg?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/replacy/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/ambv/black)\n\n<p align="center">\n<img src="./docs/replacy_ex.png" align="center" />\n</p>\n\n\n## Requirements\n\n- `spacy >= 2.0` (not installed by default, but replaCy needs to be instantiated with an `nlp` object)\n\n## Installation\n\n`pip install replacy`\n\n## Quick start\n\n```python\nfrom replacy import ReplaceMatcher\nfrom replacy.db import load_json\nimport spacy\n\n\nmatch_dict = load_json(\'/path/to/your/match/dict.json\')\n# load nlp spacy model of your choice\nnlp = spacy.load("en_core_web_sm")\n\nrmatcher = ReplaceMatcher(nlp, match_dict=match_dict)\n\n# get inflected suggestions\n# look up the first suggestion\nspan = rmatcher("She extracts revenge.")[0]\nspan._.suggestions\n# >>> [\'exacts\']\n```\n\n## Input\n\nReplaceMatcher accepts both text and spaCy doc.\n\n```python\n# text is ok\nspan = r_matcher("She extracts revenge.")[0]\n\n# doc is ok too\ndoc = nlp("She extracts revenge.")\nspan = r_matcher(doc)[0]\n```\n\n## match_dict.json format\n\nHere is a minimal `match_dict.json`:\n\n```json\n{\n  "extract-revenge": {\n    "patterns": [\n      {\n        "LEMMA": "extract",\n        "TEMPLATE_ID": 1\n      }\n    ],\n    "suggestions": [\n      [\n        {\n          "TEXT": "exact",\n          "FROM_TEMPLATE_ID": 1\n        }\n      ]\n    ],\n    "match_hook": [\n      {\n        "name": "succeeded_by_phrase",\n        "args": "revenge",\n        "match_if_predicate_is": true\n      }\n    ],\n    "test": {\n      "positive": [\n        "And at the same time extract revenge on those he so despises?",\n        "Watch as Tampa Bay extracts revenge against his former Los Angeles Rams team."\n      ],\n      "negative": ["Mother flavours her custards with lemon extract."]\n    }\n  }\n}\n```\nFor more information how to compose `match_dict` see our [wiki](https://github.com/Qordobacode/replaCy/wiki/match_dict.json-format): \n\n\n# Citing\n\nIf you use replaCy in your research, please cite with the following BibText\n\n```bibtext\n@misc{havens2019replacy,\n    title  = {SpaCy match and replace, maintaining conjugation},\n    author = {Sam Havens, Aneta Stal, and Manhal Daaboul},\n    url    = {https://github.com/Qordobacode/replaCy},\n    year   = {2019}\n}\n',
    'author': 'melisa-writer',
    'author_email': 'melisa@writer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
