# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['oplab_pipeline']

package_data = \
{'': ['*']}

install_requires = \
['argcomplete>=1.12.3',
 'argparse>=1.1',
 'colour-demosaicing>=0.1.5',
 'geographiclib>=1.50',
 'imageio>=2.6.1',
 'joblib>=0.14.1',
 'matplotlib>=3.2.1',
 'numba>=0.51.2',
 'numpy>=1.17.3',
 'opencv-python>=4.1.2',
 'pandas>=0.25.3',
 'pillow>=7.2.0',
 'plotly>=4.7.1',
 'plyfile>=0.7.2',
 'prettytable>=0.7.2',
 'psutil>=5.8.0',
 'pynmea2>=1.15.0',
 'pytz>=2019.3',
 'pyyaml>=3.12',
 'scikit-image>=0.17',
 'scipy>=1.4.1',
 'tqdm>=4.40.2',
 'wheel>=0.30.0']

setup_kwargs = {
    'name': 'oplab-pipeline',
    'version': '0.1.11',
    'description': 'Toolchain for AUV dive processing, camera calibration and image correction',
    'long_description': '[![oplab_pipeline](https://github.com/ocean-perception/oplab_pipeline/actions/workflows/oplab_pipeline.yml/badge.svg)](https://github.com/ocean-perception/oplab_pipeline/actions/workflows/oplab_pipeline.yml)\n[![Code Coverage](https://codecov.io/gh/ocean-perception/oplab_pipeline/branch/master/graph/badge.svg?token=PJBfl6qhp5)](https://codecov.io/gh/ocean-perception/oplab_pipeline) [![Documentation Status](https://readthedocs.org/projects/oplab-pipeline/badge/?version=latest)](https://oplab-pipeline.readthedocs.io/en/latest/?badge=latest)\n\n\n# oplab_pipeline\n\noplab_pipeline is a python toolchain to process AUV dives from raw data into navigation and imaging products. The software is capable of:\n\n- Process navigation: fuses AUV or ROV sensor data using state of the art filters and geolocalises recorded imagery.\n- Camera and laser calibration: performs automatic calibration pattern detection to calibrate monocular or stereo cameras. Also calibrates laser sheets with respect to the cameras.\n- Image correction: performs pixel-wise image corrections to enhance colour and contrast in underwater images.\n\nPlease review the latest changes in the [CHANGELOG.md](CHANGELOG.md). \n\n\n## Installation\n`cd` into the oplab-pipeline folder and run `pip3 install .`, resp. if you are using Anaconda run `pip install .` from the Anaconda Prompt (Anaconda3).  \nThis will make the commands `auv_nav`, `auv_cal` and `correct_images` available in the terminal. For more details refer to the documentation.\n\n\n## Documentation\nThe documentation is hosted in [read the docs](https://oplab-pipeline.readthedocs.io).\n\n\n## Citation\nIf you use this software, please cite the following article:\n\n> Yamada, T, Prügel‐Bennett, A, Thornton, B. Learning features from georeferenced seafloor imagery with location guided autoencoders. J Field Robotics. 2020; 1– 16. https://doi.org/10.1002/rob.21961\n\n\n## License\nCopyright (c) 2020, University of Southampton. All rights reserved.\n\nLicensed under the BSD 3-Clause License. \nSee LICENSE.md file in the project root for full license information.  \n\n## Developers\nPlease document the code using [Numpy Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html).\nIf you are using VSCode, there is a useful extension that helps named [Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring). Once installed, make sure you select Numpy documentation in the settings.\n',
    'author': 'Ocean Perception - University of Southampton',
    'author_email': 'miquel.massot-campos@soton.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ocean-perception/oplab_pipeline',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
