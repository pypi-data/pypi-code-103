# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opentile']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'PyTurboJPEG>=1.6.1,<2.0.0',
 'imagecodecs>=2021.8.26,<2022.0.0',
 'numpy>=1.21.2,<2.0.0',
 'tifffile>=2021.6.14,<2022.0.0']

setup_kwargs = {
    'name': 'opentile',
    'version': '0.1.1',
    'description': '[Read tiles from wsi-TIFF files]',
    'long_description': "# *opentile*\n*opentile* is a Python library for reading tiles from wsi tiff files. The aims of the proect are:\n- Allow compressed tiles to be losslessly read from wsi tiffs using 2D coordinates (tile position x, y).\n- Provide unified interface for relevant metadata.\n- Support all file formats supported by tifffile that has a non-overlapping tile structure.\n\nCrrently supported file formats are listed and described under *Supported file formats*.\n\n## Installing *opentile*\n*opentile* is available on PyPI:\n```console\n$ pip install opentile\n```\n\n## Important note\nPlease note that this is an early release and the API is not frozen yet. Function names and functionality is prone to change.\n\n## Requirements\n*opentile* requires python >=3.7 and uses numpy, Pillow, TiffFile and PyTurboJPEG (with lib-turbojpeg >= 2.1 ).\n\n## Limitations\nFiles with z-stacks are currently not fully supported.\nStriped pages with stripes divided in frames are not supported for other file except for Ndpi. This is common for overview and label images.\n\n## Supported file formats\nThe following description of the workings of the supported file formats does not include the additional specifics for each format that is handled by tifffile. Additional formats supported by tifffile and that have non-overlapping tile layout are likely to be added in future release.\n\n***Hamamatsu Ndpi***\nThe Ndpi-format uses non-rectangular tile size typically 8 pixels high, i.e. stripes. To form tiles, first multiple stripes are concatenated to form a frame covering the tile region. Second, if the stripes are longer than the tile width, the tile is croped out of the frame. The concatenation and crop transformations are performed losslessly.\n\nA ndpi-file can also contain non-tiled images. If these are part of a pyramidal series, *opentile* tiles the image.\n\n***Philips tiff***\nThe Philips tiff-format allows tiles to be sparse, i.e. missing. For such tiles, *opentile* instead provides a blank (currently white) tile image using the same jpeg header as the rest of the image.\n\n***Aperio svs***\nSome Asperio svs-files have corrupt tile data at edges of non-base pyramidal levels. This is observed as tiles with 0-byte length and tiles with incorrect pixel data. *opentile* detects such corruption and instead returns downscaled image data from lower levels. Associated images (label, overview) are currently not handled correctly.\n\n## Basic usage\n***Load a Ndpi-file using tile size (1024, 1024) pixels.***\n```python\nfrom opentile import OpenTile\ntile_size = (1024, 1024)\nturbo_path = 'C:/libjpeg-turbo64/bin/turbojpeg.dll'\ntiler = OpenTile.open(path_to_ndpi_file, tile_size, turbo_path)\n```\n\n***Get rectangular tile at level 0 and position x=0, y=0.***\n```python\ntile = tiler.get_tile(0, (0, 0))\n```\n\n***Close the tiler object.***\n```python\ntiler.close()\n```\n## Other TIFF python tools\n- [tifffile](https://github.com/cgohlke/tifffile)\n- [tiffslide](https://github.com/bayer-science-for-a-better-life/tiffslide)\n\n## Contributing\nWe welcome any contributions to help improve this tool for the WSI community!\n\nWe recommend first creating an issue before creating potential contributions to check that the contribution is in line with the goals of the project. To submit your contribution, please issue a pull request on the imi-bigpicture/opentile repository with your changes for review.\n\nOur aim is to provide constructive and positive code reviews for all submissions. The project relies on gradual typing and roughly follows PEP8. However, we are not dogmatic. Most important is that the code is easy to read and understand.\n\n## Acknowledgement\n*opentile*: Copyright 2021 Sectra AB, licensed under Apache 2.0.\n\nThis project is part of a project that has received funding from the Innovative Medicines Initiative 2 Joint Undertaking under grant agreement No 945358. This Joint Undertaking receives support from the European Union’s Horizon 2020 research and innovation programme and EFPIA. IMI website: www.imi.europa.eu",
    'author': 'Erik O Gabrielsson',
    'author_email': 'erik.o.gabrielsson@sectra.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imi-bigpicture/opentile',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
