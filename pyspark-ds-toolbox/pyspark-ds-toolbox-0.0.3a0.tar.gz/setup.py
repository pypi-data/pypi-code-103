# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyspark_ds_toolbox',
 'pyspark_ds_toolbox.causal_inference',
 'pyspark_ds_toolbox.ml']

package_data = \
{'': ['*']}

install_requires = \
['numpy==1.21.0',
 'pandas>=1.3.4,<2.0.0',
 'pyspark>=3.1.1,<4.0.0',
 'typeguard>=2.13.2,<3.0.0']

setup_kwargs = {
    'name': 'pyspark-ds-toolbox',
    'version': '0.0.3a0',
    'description': 'A Pyspark companion for data science tasks.',
    'long_description': '# Pyspark DS Toolbox\n\nThe objective of the package is to provide tools that helps the daily work of data science with spark.\n\n## Package Structure\n```\npyspark-ds-toolbox\n├─ .git/\n├─ .github\n│  └─ workflows\n│     └─ package-tests.yml\n├─ .gitignore\n├─ LICENSE.md\n├─ README.md\n├─ examples\n│  └─ ml_eval_estimate_shapley_values.ipynb\n├─ poetry.lock\n├─ pyproject.toml\n├─ docs/\n├─ pyspark_ds_toolbox\n│  ├─ __init__.py\n│  ├─ causal_inference\n│  │  ├─ __init__.py\n│  │  ├─ diff_in_diff.py\n│  │  └─ ps_matching.py\n│  ├─ ml\n│  │  ├─ __init__.py\n│  │  ├─ data_prep.py\n│  │  └─ eval.py\n│  └─ wrangling.py\n├─ requirements.txt\n└─ tests\n   ├─ __init__.py\n   ├─ conftest.py\n   ├─ data\n   ├─ test_causal_inference\n   │  ├─ test_diff_in_diff.py\n   │  └─ test_ps_matching.py\n   ├─ test_ml\n   │  ├─ test_data_prep.py\n   │  └─ test_ml_eval.py\n   ├─ test_pyspark_ds_toolbox.py\n   └─ test_wrangling.py\n```',
    'author': 'vinicius.sousa',
    'author_email': 'vinisousa04@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/viniciusmsousa/pyspark-ds-toolbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
