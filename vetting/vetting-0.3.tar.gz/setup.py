# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vetting']

package_data = \
{'': ['*']}

install_requires = \
['corner>=2.1.0,<3.0.0', 'lightkurve>=2.0.9']

setup_kwargs = {
    'name': 'vetting',
    'version': '0.3',
    'description': 'Simple, stand-alone vetting tools for transiting signals in Keper, K2 and TESS data',
    'long_description': "# vetting\n\n**`vetting` contains simple, stand-alone Python tools for vetting transiting signals in NASA's Kepler, K2 and TESS data. `vetting` requires an installation of Python 3.8 or higher.**\n\n[![pypi](https://img.shields.io/pypi/v/vetting)](https://pypi.org/project/vetting/)\n![pytest](https://github.com/ssdatalab/vetting/workflows/pytest/badge.svg)\n\n## Installation\n\nYou can install `vetting` by executing the following in a terminal\n\n```\npip install vetting\n```\n\n### Centroid testing\n\nAn example of a simple test is shown below.\n\n![Example of simple centroid test](https://github.com/SSDataLab/vetting/raw/main/demo.png)\n\nHere a significant offset is detected in the centroid of false positive KOI-608 during transit. The p-value for the points during transit being drawn from the same distribution as the points out of transit is low, (there is a less than 1% chance these are drawn from the same distribution). To recreate this example you can use the following script:\n\n```python\nimport lightkurve as lk\nfrom vetting import centroid_test\n\ntpf = lk.search_targetpixelfile('KOI-608', mission='Kepler', quarter=10).download()\nperiod, t0, dur = 25.3368592, 192.91552, 8.85/24\nr = centroid_test(tpf, period, t0, dur, aperture_mask='pipeline', plot=False)\n```\n",
    'author': 'Christina Hedges',
    'author_email': 'christina.l.hedges@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SSDataLab/vetting',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
