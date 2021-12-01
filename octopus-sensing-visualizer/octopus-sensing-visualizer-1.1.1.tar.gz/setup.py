# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['octopus_sensing_visualizer', 'octopus_sensing_visualizer.prepare_data']

package_data = \
{'': ['*'], 'octopus_sensing_visualizer': ['ui_build/*']}

install_requires = \
['CherryPy>=18.6.0,<19.0.0',
 'heartpy>=1.2.7,<2.0.0',
 'neurokit>=0.2.0,<0.3.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.2.5,<2.0.0',
 'pycairo>=1.20.1,<2.0.0']

entry_points = \
{'console_scripts': ['octopus-sensing-visualizer = '
                     'octopus_sensing_visualizer.main:main']}

setup_kwargs = {
    'name': 'octopus-sensing-visualizer',
    'version': '1.1.1',
    'description': 'Library for visualizing data synchronously recorded from different sensors',
    'long_description': 'Octopus Sensing Visualizer\n==========================\n\nOctopus Sensing Visualizer is a web-based real-time visualizer for [Octopus Sensing](https://octopus-sensing.nastaran-saffar.me/). \nIt can be used for offline data visualization. You can visualize the recorded multimodal data as the raw data. Also, it can extract\nsome essential features or components of data and display them in a single window. Using this tool, you can observe the effect of an event on recorded data simultaneously.\n\n[Octopus Sensing Visualizer](https://github.com/octopus-sensing/octopus-sensing-visualizer) is \na separated project and can be installed if we need to visualize data. \nIt can be used for displaying recorded data with\nthe same format as we recorded through Octopus Sensing.\n\n**To see the full documentation go to [Otopus Sensing](https://octopus-sensing.nastaran-saffar.me/visualizer) website.**\n\nCopyright\n---------\n\nCopyright © 2021 [Nastaran Saffaryazdi]\n\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU\nGeneral Public License as published by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nSee [License file](https://github.com/nastaran62/octopus-sensing/blob/master/LICENSE)  for full terms.',
    'author': 'Nastaran Saffaryazdi',
    'author_email': 'nsaffar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://octopus-sensing.nastaran-saffar.me',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
