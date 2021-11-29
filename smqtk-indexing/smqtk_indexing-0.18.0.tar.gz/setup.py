# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smqtk_indexing',
 'smqtk_indexing.impls',
 'smqtk_indexing.impls.hash_index',
 'smqtk_indexing.impls.lsh_functor',
 'smqtk_indexing.impls.nn_index',
 'smqtk_indexing.interfaces',
 'smqtk_indexing.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.5,<2.0.0',
 'scipy>=1.5.2,<2.0.0',
 'smqtk-core>=0.18.0',
 'smqtk-dataprovider>=0.16.0',
 'smqtk-descriptors>=0.18.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.8,<0.9'],
 'faiss': ['faiss-cpu>=1.7.0,<2.0.0'],
 'sklearn': ['scikit-learn>=0.24.1,<0.25.0']}

entry_points = \
{'smqtk_plugins': ['smqtk_indexing.impls.hash_index.linear = '
                   'smqtk_indexing.impls.hash_index.linear',
                   'smqtk_indexing.impls.hash_index.sklearn_balltree = '
                   'smqtk_indexing.impls.hash_index.sklearn_balltree',
                   'smqtk_indexing.impls.lsh_functor.itq = '
                   'smqtk_indexing.impls.lsh_functor.itq',
                   'smqtk_indexing.impls.lsh_functor.simple_rp = '
                   'smqtk_indexing.impls.lsh_functor.simple_rp',
                   'smqtk_indexing.impls.nn_index.faiss = '
                   'smqtk_indexing.impls.nn_index.faiss',
                   'smqtk_indexing.impls.nn_index.flann = '
                   'smqtk_indexing.impls.nn_index.flann',
                   'smqtk_indexing.impls.nn_index.lsh = '
                   'smqtk_indexing.impls.nn_index.lsh',
                   'smqtk_indexing.impls.nn_index.mrpt = '
                   'smqtk_indexing.impls.nn_index.mrpt']}

setup_kwargs = {
    'name': 'smqtk-indexing',
    'version': '0.18.0',
    'description': 'Algorithms, data structures and utilities around computingdescriptor k-nearest-neighbors.',
    'long_description': "# SMQTK - Indexing\n\nThis package provides interfaces and implementations around the\nk-nearest-neighbor algorithm.\n\nThis package defines interfaces and implementations around efficient,\nlarge-scale indexing of descriptor vectors.\nThe sources of such descriptor vectors may come from a multitude of sources,\nsuch as hours of video archives.\nSome provided implementation plugins include [Locality-sensitive Hashing\n(LSH)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) and FAIR's\n[FAISS] library.\n\n## Documentation\nYou can build the sphinx documentation locally for the most up-to-date\nreference:\n```bash\n# Install dependencies\npoetry install\n# Navigate to the documentation root.\ncd docs\n# Build the docs.\npoetry run make html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n",
    'author': 'Kitware, Inc.',
    'author_email': 'smqtk-developers@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kitware/SMQTK-Indexing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
