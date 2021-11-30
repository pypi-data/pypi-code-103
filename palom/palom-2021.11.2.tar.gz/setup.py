# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['palom', 'palom.cli', 'palom.cli.schema']

package_data = \
{'': ['*']}

install_requires = \
['dask>=2021.10.0,<2022.0.0',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib>=3.4.3,<4.0.0',
 'napari-lazy-openslide>=0.2.0,<0.3.0',
 'numpy>=1.21.3,<2.0.0',
 'opencv-python>=4.5.3.56,<5.0.0.0',
 'scikit-image>=0.18.3,<0.19.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.7.1,<2.0.0',
 'tifffile>=2021.10.12,<2022.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'yamale>=4.0.2,<5.0.0',
 'zarr>=2.10.0,<3.0.0']

entry_points = \
{'console_scripts': ['palom-svs = palom.cli.svs:main',
                     'palom-svs-helper = palom.cli.helper:main']}

setup_kwargs = {
    'name': 'palom',
    'version': '2021.11.2',
    'description': 'Piecewise alignment for layers of mosaics',
    'long_description': '# Piecewise alignment for layers of mosaics\n\nPalom started as a tool for registering [whole-slide\nimages](https://en.wikipedia.org/wiki/Digital_pathology) of the same [FFPE\nsection](https://en.wikipedia.org/wiki/Histology#Sample_preparation) with\ndifferent [IHC stainings](https://en.wikipedia.org/wiki/Immunohistochemistry).\n\n---\n\n## Installation\n\nInstalling palom in a fresh conda environment is recommended. [Instruction for\ninstalling miniconda](https://docs.conda.io/en/latest/miniconda.html)\n\n### Step 1\n\nCreate a named conda environment - _palom_, in the following example, and activate the environment.\n\n```\nconda create -n palom python=3.7 pip -c conda-forge\nconda activate palom\n```\n\n### Step 2\n\nInstall openslide in the conda environment.\n\n```\nconda install openslide -c sdvillal\n```\n\n### Step 3\n\nInstall palom from pypi in the conda environment.\n\n```\npython -m pip install palom\n```\n\n---\n\n## CLI usage\n\n### Configuration YAML file\n\nPalom CLI tool merges multiple SVS files into a pyramidal OME-TIFF file, with\nthe option to perform preset stain separation (4 modes are available - `output\nmode`: `hematoxylin`, `aec`, `grayscale`, `color`)\n\nA user-defined configuration YAML file is required for the run. A configuration\nexample can be printed to the console by running\n\n```bash\npalom-svs show example\n```\n\n```yaml\ninput dir: Y:\\user\\me\\projects\\data\\mihc\noutput full path: Y:\\user\\me\\projects\\analysis\\mihc\\2021\\skin-case-356.ome.tif\n\nreference image:\n    filename: 20210111/skin_case_356_HEM_C11R3_HEM.svs\n    output mode: hematoxylin\n    channel name: Hematoxylin\n\nmoving images:\n- filename: 20210101/skin_case_356_HEM_C01R1_PD1.svs\n  output mode: aec\n  channel name: PD-1\n- filename: 20210101/skin_case_356_HEM_C01R2_PDL1.svs\n  output mode: aec\n  channel name: PD-L1\n```\n\nTo show the configuration schema, run the following command\n\n```bash\npalom-svs show schema\n```\n\n### Use the helper script to generate the configuration file\n\n[A helper\nscript](https://github.com/Yu-AnChen/palom/blob/main/palom/cli/helper.py) is\nincluded showing how to automatically generate the configuration file if the SVS\nfiles are organized and have specific naming pattern.\n\nHere\'s an example directory containing many SVS files\n\n```\nY:\\DATA\\SARDANA\\MIHC\\768473\\RAW\n    CBB_SARDANA_768473_C04R1_CD8.svs\n    KB_SARDANA_768473_C01R1_PD1.svs\n    KB_SARDANA_768473_C01R2_PDL1.svs\n    KB_SARDANA_768473_C01R3_Hem.svs\n    KB_SARDANA_768473_C02R1_CD4.svs\n    KB_SARDANA_768473_C03R1_CD3.svs\n    KB_SARDANA_768473_C03R3_DCLAMP.svs\n```\n\nRunning the following command to generate the configuration file\n\n```bash\npalom-svs-helper -i "Y:\\DATA\\SARDANA\\MIHC\\768473\\RAW" -n "*Hem*" -o "Y:\\DATA\\SARDANA\\MIHC\\768473\\RAW\\palom\\768473.ome.tif" -c "Y:\\DATA\\SARDANA\\MIHC\\768473\\768473.yml"\n```\n\nAnd the resulting `Y:\\DATA\\SARDANA\\MIHC\\768473\\768473.yml` file \n\n```yaml\ninput dir: Y:\\DATA\\SARDANA\\MIHC\\768473\\RAW\noutput full path: Y:\\DATA\\SARDANA\\MIHC\\768473\\RAW\\palom\\768473.ome.tif\nreference image:\n  filename: .\\KB_SARDANA_768473_C01R3_Hem.svs\n  output mode: hematoxylin\n  channel name: Hem-C01R3\nmoving images:\n- filename: .\\KB_SARDANA_768473_C01R1_PD1.svs\n  output mode: aec\n  channel name: PD1-C01R1\n- filename: .\\KB_SARDANA_768473_C01R2_PDL1.svs\n  output mode: aec\n  channel name: PDL1-C01R2\n- filename: .\\KB_SARDANA_768473_C02R1_CD4.svs\n  output mode: aec\n  channel name: CD4-C02R1\n- filename: .\\KB_SARDANA_768473_C03R1_CD3.svs\n  output mode: aec\n  channel name: CD3-C03R1\n- filename: .\\KB_SARDANA_768473_C03R3_DCLAMP.svs\n  output mode: aec\n  channel name: DCLAMP-C03R3\n- filename: .\\CBB_SARDANA_768473_C04R1_CD8.svs\n  output mode: aec\n  channel name: CD8-C04R1\n```\n\nAfter reviewing the configuration file, process those SVS files by running\n\n```bash\npalom-svs run -c "Y:\\DATA\\SARDANA\\MIHC\\768473\\768473.yml"\n```\n\nWhen the process is finished, a pyramidal OME-TIFF file will be generated along\nwith PNG files showing the feature-based registration results and a log file. \n\n```\nY:\\DATA\\SARDANA\\MIHC\\768473\\RAW\n│   CBB_SARDANA_768473_C04R1_CD8.svs\n│   KB_SARDANA_768473_C01R1_PD1.svs\n│   KB_SARDANA_768473_C01R2_PDL1.svs\n│   KB_SARDANA_768473_C01R3_Hem.svs\n│   KB_SARDANA_768473_C02R1_CD4.svs\n│   KB_SARDANA_768473_C03R1_CD3.svs\n│   KB_SARDANA_768473_C03R3_DCLAMP.svs\n│\n└───palom\n    │   768473.ome.tif\n    │\n    └───qc\n            01-KB_SARDANA_768473_C01R1_PD1.svs.png\n            02-KB_SARDANA_768473_C01R2_PDL1.svs.png\n            03-KB_SARDANA_768473_C02R1_CD4.svs.png\n            04-KB_SARDANA_768473_C03R1_CD3.svs.png\n            05-KB_SARDANA_768473_C03R3_DCLAMP.svs.png\n            06-CBB_SARDANA_768473_C04R1_CD8.svs.png\n            768473.ome.tif.log\n```\n\n---\n\n## Scripting\n\n__WARNING__ API may change in the future\n\n### For SVS files\n\n```python\nimport palom\n\nc1r = palom.reader.SvsReader(r\'Y:\\DATA\\SARDANA\\MIHC\\75684\\GG_TNP_75684_D21_C11R3_HEM.svs\')\nc2r = palom.reader.SvsReader(r\'Y:\\DATA\\SARDANA\\MIHC\\75684\\GG_TNP_75684_D23_C01R1_PD1.svs\')\n\nc1rp = palom.color.PyramidHaxProcessor(c1r.pyramid, thumbnail_level=2)\nc2rp = palom.color.PyramidHaxProcessor(c2r.pyramid, thumbnail_level=2)\n\nLEVEL = 1\nc21l = palom.align.Aligner(\n    c1rp.get_processed_color(LEVEL), \n    c2rp.get_processed_color(LEVEL),\n    ref_thumbnail=c1rp.get_processed_color(2).compute(),\n    moving_thumbnail=c2rp.get_processed_color(2).compute(),\n    ref_thumbnail_down_factor=c1r.level_downsamples[2] / c1r.level_downsamples[LEVEL],\n    moving_thumbnail_down_factor=c2r.level_downsamples[2] / c2r.level_downsamples[LEVEL]\n)\n\nc21l.coarse_register_affine()\nc21l.compute_shifts()\nc21l.constrain_shifts()\n\nc21l.block_affine_matrices_da\n\nc2m = palom.align.block_affine_transformed_moving_img(\n    c1rp.get_processed_color(LEVEL),\n    c2rp.get_processed_color(LEVEL, \'aec\'),\n    mxs=c21l.block_affine_matrices_da\n)\n\npalom.pyramid.write_pyramid(\n    palom.pyramid.normalize_mosaics([c2m]),\n    r"Y:\\DATA\\SARDANA\\MIHC\\75684\\mosaic.ome.tif"\n)\n```\n\n### For OME-TIFF files\n\n```python\nimport palom\n\nc1r = palom.reader.OmePyramidReader(r"Z:\\P37_Pilot2\\P37_S12_Full.ome.tiff")\nc2r = palom.reader.OmePyramidReader(r"Z:\\P37_Pilot2\\HE\\P37_S12_E033_93_HE.ome.tiff")\n\nLEVEL = 1\nc21l = palom.align.Aligner(\n    c1r.read_level_channels(LEVEL, 0),\n    c2r.read_level_channels(LEVEL, 1),\n    c1r.read_level_channels(3, 0).compute(),\n    c2r.read_level_channels(3, 1).compute(),\n    c1r.level_downsamples[3] / c1r.level_downsamples[LEVEL],\n    c2r.level_downsamples[3] / c2r.level_downsamples[LEVEL]\n)\n\nc21l.coarse_register_affine(n_keypoints=4000)\nc21l.compute_shifts()\nc21l.constrain_shifts()\n\nc2m = palom.align.block_affine_transformed_moving_img(\n    c1r.read_level_channels(LEVEL, 0),\n    c2r.pyramid[LEVEL],\n    mxs=c21l.block_affine_matrices_da\n)\n\npalom.pyramid.write_pyramid(\n    palom.pyramid.normalize_mosaics([\n        c1r.read_level_channels(LEVEL, [0, 1, 2]),\n        c2m\n    ]),\n    r"Z:\\P37_Pilot2\\mosaic.ome.tif"\n)\n```',
    'author': 'Yu-An Chen',
    'author_email': 'atwood12@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://pypi.org/project/palom/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.8,<3.8',
}


setup(**setup_kwargs)
