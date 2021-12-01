from pathlib import Path

import numpy as np

from .helpers import read_raster_image
from .helpers import get_file_name
from .metas import SpectralIndexMeta
from .exceptions import InvalidNoDataValueError


class SpectralIndex:
    '''Class for calculating spectral indices.

    Attributes
    ----------
    bands : dict
        dictionary containing Sentinel 2 bands
    meta : SpectralIndexMeta
        metadata for spectral index


    '''

    def __init__(self, bands: dict) -> None:
        '''SpectralIndex instance.

        Parameters
        ----------
        bands: dict

        '''
        self.bands = bands
        self.meta = SpectralIndexMeta(self.bands['blue']).get_meta()


    def calculate_index(self):
        pass


class AWEI(SpectralIndex):
    '''Class for calculating Advanced Water Extraction Index (AWEI).

    Methods
    -------
    calculate_index()
    '''

    def __init__(self, bands: dict) -> None:
        super().__init__(bands)

    def calculate_index(self) -> np.ndarray:
        '''Advanced water extraction index

        AWEI = 4 * (GREEN - SWIR 1) - (0.25 * NIR + 2.75 * SWIR 2)

        Returns
        ----------
        numpy array

        '''

        green = read_raster_image(self.bands['green'], as_float=True)
        swir_1 = read_raster_image(self.bands['swir_1'], as_float=True)
        nir = read_raster_image(self.bands['nir'], as_float=True)
        swir_2 = read_raster_image(self.bands['swir_2'], as_float=True)

        awei = (4 * (green - swir_1) - (0.25 * nir + 2.75 * swir_2))

        return awei


class NDVI(SpectralIndex):
    '''Class for calculating Normalized Difference Vegetation Index (NDVI).


    Methods
    -------
    calculate_index()
    '''

    def __init__(self, bands: dict) -> None:
        super().__init__(bands)

    def calculate_index(self) -> np.ndarray:
        '''Normalized difference vegetation index

        NDVI = (NIR - RED) / (NIR + RED)

        Returns
        ----------
        numpy array

        '''

        nir = read_raster_image(self.bands['nir'], as_float=True)
        red = read_raster_image(self.bands['red'], as_float=True)

        ndvi = (nir - red) / (nir + red)

        return ndvi


class BAEI(SpectralIndex):
    '''Class for calculating Built-up Area Extraction Index (BAEI).

    Methods
    -------
    calculate_index()
    '''

    def __init__(self, bands: dict) -> None:
        super().__init__(bands)

    def calculate_index(self) -> np.ndarray:
        '''Built-up area extraction index

        BAEI = (RED + 0.3) / (GREEN + SWIR 1)

        Returns
        ----------
        numpy array

        '''

        red = read_raster_image(self.bands['red'], as_float=True)
        green = read_raster_image(self.bands['green'], as_float=True)
        swir_1 = read_raster_image(self.bands['swir_1'], as_float=True)

        baei = (red + 0.3) / (green + swir_1)

        return baei


class NDTI(SpectralIndex):
    '''Class for calculating Normalized Difference Tillage Index (NDTI).


    Methods
    -------
    calculate_index()
    '''

    def __init__(self, bands: dict) -> None:
        super().__init__(bands)

    def calculate_index(self) -> np.ndarray:
        '''Normalized difference tillage index

        NDTI = (SWIR 1 - SWIR 2) / (SWIR 1 + SWIR 2)

        Returns
        ----------
        numpy array

        '''

        swir_1 = read_raster_image(self.bands['swir_1'], as_float=True)
        swir_2 = read_raster_image(self.bands['swir_2'], as_float=True)

        ndti = (swir_1 - swir_2) / (swir_1 + swir_2)

        return ndti


class SpectralIndexFactory:
    '''Factory for creating spectral index
    
    Methods
    -------
    get_spectral_index(spec_index: str, bands: dict)
        returns spectral index
    
    '''

    def get_spectral_index(self, spec_index: str, bands: dict) -> SpectralIndex:
        '''Returns SpectralIndexFactory object based specified spectral index.

        Parameters
        ----------
        spec_index: str

        bands: dict

        Returns:
        ----------
        SpectralIndex
        '''
        
        if spec_index == 'AWEI':
            return AWEI(bands)
        elif spec_index == 'NDVI':
            return NDVI(bands)
        elif spec_index == 'BAEI':
            return BAEI(bands)
        elif spec_index == 'NDTI':
            return NDTI(bands)


def set_no_data_to_99999(spec_index: np.ndarray, no_data: str) -> np.ndarray:
    '''Spectral index values that represent no data (0, Nan or infinite) are set to high value of 99 999.
    This is for better separation of no data values in k means classification.

    Parameters
    ----------
    spec_index: numpy array

    no_data: str

    Returns
    ----------
    numpy array

    Raises 
    ----------
    InvalidNoDataValueError

    '''

    if no_data == '0':
        return np.where(spec_index == 0, 99999, spec_index)
    elif no_data == 'nan':
        return np.where(np.isnan(spec_index), 99999, spec_index)
    elif no_data == 'inf':
        return np.where(np.isinf(spec_index), 99999, spec_index)
    else:
        raise InvalidNoDataValueError(feature='no_data', value=no_data,
                                      message='Invalid no data value. Possible options are 0, inf and nan')


def get_spectral_index_files(product_path : str) -> dict:
    '''Returns file paths for calculated spectral indices.

    Parameters
    ----------
    product_path : str

    Returns
    ----------
    dict 
    '''

    product_name = get_file_name(product_path)
    spec_index_files = [
        f'_spec_index/AWEI_{product_name}.tif',
        f'_spec_index/NDVI_{product_name}.tif',
        f'_spec_index/BAEI_{product_name}.tif',
        f'_spec_index/NDTI_{product_name}.tif'
    ]

    return {
        'AWEI': Path(spec_index_files[0]),
        'NDVI': Path(spec_index_files[1]),
        'BAEI': Path(spec_index_files[2]),
        'NDTI': Path(spec_index_files[3])
    }

def get_spectral_index_no_data_values() -> dict:
    '''Returns no data values for spectral indices.

    Returns
    ----------
    dict
    '''
    return {
        'AWEI': '0',
        'NDVI': 'nan',
        'BAEI': 'inf',
        'NDTI': 'nan'
    }