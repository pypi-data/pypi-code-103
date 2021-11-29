# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opensoundscape',
 'opensoundscape.preprocess',
 'opensoundscape.resources',
 'opensoundscape.torch',
 'opensoundscape.torch.architectures',
 'opensoundscape.torch.models']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2<3.0',
 'docopt>=0.6.2',
 'ipykernel>=5.2.0',
 'ipython>=7.10',
 'jupyterlab>=2.1.4',
 'librosa>=0.7.0',
 'matplotlib>=3.2.1',
 'numba>=0.48.0',
 'pandas>=1.0.3',
 'pywavelets>=1.2.0',
 'ray>=0.8.5',
 'schema>=0.7.2',
 'scikit-image>=0.17.2',
 'scikit-learn>=0.24.2',
 'tinytag>=1.6.0',
 'torch>=1.8.1',
 'torchvision>=0.9.1']

entry_points = \
{'console_scripts': ['build_docs = opensoundscape.console:build_docs',
                     'opensoundscape = opensoundscape.console:entrypoint']}

setup_kwargs = {
    'name': 'opensoundscape',
    'version': '0.6.0',
    'description': 'Open source, scalable acoustic classification for ecology and conservation',
    'long_description': "[![CI Status](https://github.com/kitzeslab/opensoundscape/workflows/CI/badge.svg)](https://github.com/kitzeslab/opensoundscape/actions?query=workflow%3ACI)\n[![Documentation Status](https://readthedocs.org/projects/opensoundscape/badge/?version=latest)](http://opensoundscape.org/en/latest/?badge=latest)\n\n# OpenSoundscape\n\nOpenSoundscape is a utility library for analyzing bioacoustic data. It consists of Python modules for tasks such as preprocessing audio data, training machine learning models to classify vocalizations, estimating the spatial location of sounds, identifying which species' sounds are present in acoustic data, and more.\n\nThese utilities can be strung together to create data analysis pipelines. OpenSoundscape is designed to be run on any scale of computer: laptop, desktop, or computing cluster.\n\nOpenSoundscape is currently in active development. If you find a bug, please submit an issue. If you have another question about OpenSoundscape, please email Sam Lapp (`sam.lapp` at `pitt.edu`) or Tessa Rhinehart (`tessa.rhinehart` at `pitt.edu`).\n\n# Installation\n\nOpenSoundscape can be installed on Windows, Mac, and Linux machines. It has been tested on Python 3.7 and 3.8.\n\nMost users should install OpenSoundscape via pip: `pip install opensoundscape==0.6.0`. Contributors and advanced users can also use Poetry to install OpenSoundscape.\n\nFor more detailed instructions on how to install OpenSoundscape and use it in Jupyter, see the [documentation](http://opensoundscape.org).\n\n# Features & Tutorials\nOpenSoundscape includes functions to:\n* trim, split, and manipulate audio files\n* create and manipulate spectrograms\n* train binary CNNs on spectrograms with PyTorch\n* run pre-trained CNNs to detect vocalizations\n* detect periodic vocalizations with RIBBIT\n* spatially locate sounds\n* manipulate Raven annotations\n\nOpenSoundscape can also be used with our library of publicly available trained machine learning models for the detection of 500 common North American bird species.\n\nFor full API documentation and tutorials on how to use OpenSoundscape to work with audio and spectrograms, train machine learning models, apply trained machine learning models to acoustic data, and detect periodic vocalizations using RIBBIT, see the [documentation](http://opensoundscape.org).\n",
    'author': 'Justin Kitzes',
    'author_email': 'justin.kitzes@pitt.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jkitzes/opensoundscape',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
