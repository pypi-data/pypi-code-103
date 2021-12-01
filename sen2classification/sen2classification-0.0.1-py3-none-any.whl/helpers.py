import os
from pathlib import Path
from typing import Union
import shutil

import numpy as np
import rasterio
from rasterio.enums import Resampling

from .metas import ResampledMeta

ROOT = Path.cwd()


def create_dir(dirname: str) -> None:
    '''Creates a directory in cwd.

    Parameters
    ----------
    dirname : str
    '''

    if not Path(ROOT, dirname).exists():
        os.mkdir(Path(ROOT, dirname))


def validate_dir(dirname: str) -> str:
    '''Check if directory is in cwd.
    Return directory path as string.

    Parameters
    ----------
    dirname : str

    Raises
    ----------
    FileNotFoundError
    '''
    if Path(ROOT, dirname).exists():
        return str(Path(ROOT, dirname))
    raise FileNotFoundError(f'No directory {dirname} in {ROOT}.')


def get_file_name(path: str) -> str:
    '''Removes .SAFE extension from Sentinel 2 product name.

    Parameters
    ----------
    path : str

    Returns
    ----------
    str
    '''
    name = Path(path).name
    if '.SAFE' in name:
        return name.split('.')[0]
    return name


def read_raster_image(input_file: Union[str, Path], as_float: bool = False, only_first: bool = False) -> np.ndarray:
    '''Reads raster image as numpy array. If only_first is set returns only first band in multiband image.
    If as_float is set reads raster image values as float 32.

    input_file : str, Path

    as_float : bool

    only_first : bool

    Returns
    ----------
    numpy array
    '''
    with rasterio.open(input_file) as src:
        if only_first:
            raster = src.read(1)
        else:
            raster = src.read()
        if as_float:
            return raster.astype('float32')
        return raster


def save_raster_image(input_raster: np.ndarray, output_file: Union[str, Path], meta: dict) -> None:
    '''Saves raster image as .tif file.

    Parameters
    ----------
    input_raster : numpy array

    output_file : str

    meta : dict
    '''
    with rasterio.open(output_file, 'w', **meta) as out:
        out.write(input_raster.astype(meta['dtype']))


def get_resampled_swir_files(product_path: str) -> dict:
    '''Returns file paths for resampled swir bands.

    Returns
    ----------
    dict
    '''

    product_name = get_file_name(product_path)
    resampled_files = [
        f'_resampled/SWIR_1_{product_name}.tif',
        f'_resampled/SWIR_2_{product_name}.tif'
    ]

    return {
        'swir_1': Path(resampled_files[0]),
        'swir_2': Path(resampled_files[1])
    }


def get_classification_raster_file(product_path: str, classification: str) -> Path:
    '''Returns classification raster file path.

    Returns
    ----------
    Path
    '''
    product_name = get_file_name(product_path)
    return Path(f'{classification}_{product_name}.tif').resolve()


def get_label_raster_file(product_path: str) -> Path:
    '''Returns label raster file path.

    Returns
    ----------
    Path
    '''
    product_name = get_file_name(product_path)
    return Path(f'label_raster_{product_name}.tif').resolve()


def get_nodata_values(input_raster: str) -> np.ndarray:
    '''Extracts no data pixels from image, i.e. pixels with value 0 in color bands.

    Parameters
    ----------
    input_raster: str

    Returns
    ----------
    numpy array
    '''
    raster = read_raster_image(input_raster)
    return np.where(raster == 0, 0, 1)


def run_cleanup() -> None:
    '''Deletes all directories containing rasters created during classification intermediate steps, i.e. resampled swir rasters.
    '''
    dirs_to_remove = ['_k_means', '_land_cover', '_resampled', '_spec_index']
    file_to_remove = 'label_raster'

    cwd = Path.cwd()

    for dir in cwd.iterdir():
        if file_to_remove in str(dir):
            os.remove(dir)
        if dir.is_dir():
            if dir.name in dirs_to_remove:
                shutil.rmtree(dir)


class ResampledRaster:
    '''Class for resampling raster to target resolution. Method used for resampling is bilinear.

    Attributes
    ----------
    raster_to_resample : string
        file path.
    target_raster : string
        file path.
    meta : ResampledMeta
        metadata for resampled raster

    Methods
    -------
    get_resampled_raster()
        returns raster resampled to 10m

    '''

    def __init__(self, raster_to_resample: str, target_raster: str):
        '''ResampledRaster instance.

        Parameters
        ----------
        raster_to_resample : str
            file path.
        target_raster : str
            file path.

        '''
        self.raster_to_resample = raster_to_resample
        self.target_raster = target_raster
        self.meta = ResampledMeta(self.target_raster).get_meta()

    def _resample(self) -> np.ndarray:
        '''Applies bilinear interpolation on raster image.

        Returns
        ----------
        numpy array
        '''
        with rasterio.open(self.raster_to_resample) as src:
            raster_resampled = src.read(
                out_shape=(
                    src.count,
                    self.meta['height'],
                    self.meta['width']
                ),
                resampling=Resampling.bilinear
            )
            return raster_resampled

    def get_resampled_raster(self) -> np.ndarray:
        '''Returns 10m resampled raster masked with nodata mask.

        Returns
        ----------
        numpy array
        '''
        resampled_raster = self._resample()
        nodata_mask = get_nodata_values(self.target_raster)
        # Masking is necessary because bilinear interpolation sets valid pixel values where no data pixels are
        # (on the line separating valid pixels from no data ones)
        resampled_raster_no_data_mask = resampled_raster * nodata_mask
        return resampled_raster_no_data_mask
