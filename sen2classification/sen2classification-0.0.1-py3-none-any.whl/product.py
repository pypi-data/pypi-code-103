from pathlib import Path
import zipfile
from typing import Optional

import numpy as np

from .bands import BandsFactory 
from .spectral_index import SpectralIndexFactory
from .spectral_index import set_no_data_to_99999
from .spectral_index import get_spectral_index_files
from .spectral_index import get_spectral_index_no_data_values
from .exceptions import InvalidProductError 
from .exceptions import InvalidProductTypeError
from .exceptions import BandNotResampledError
from .helpers import create_dir
from .helpers import ResampledRaster
from .helpers import save_raster_image
from .helpers import get_resampled_swir_files


np.seterr(divide='ignore', invalid='ignore')


class Sentinel2Product:
    '''A class for setting up Sentinel 2 product for classification.

    Attributes
    ----------
    product : str
        sentinel 2 product
    product_type : str
        sentinel 2 product type
    bands : dict
        dictionary containing band file paths 
    spectral_index: dict
        dictionary containing spectral file paths

    Methods
    -------
    setup_bands()
        setting up Sentinel 2 band file paths

    resample_swir_to_10m()
        resampling swir 1 and swir 2 from 20m resolution to 10m

    calculate_spectral_indices()
        calculating spectral indices necessary for image classification

    '''

    def __init__(self, product: str, product_type: Optional[str] = None) -> None:
        '''Sentinel 2 product instance.

        Parameters
        ----------
        product : str

        product_type: str

        '''
        self.product = product
        self.product_type = product_type
        self.bands: dict = {}
        self.spectral_index: dict = {}
        self._set_up_steps = {
            'Bands setup': False,
            'Swir resampling': False,
            'Spectral indices calculation': False
        }

    @property
    def product(self) -> str:
        return self._product

    @product.setter
    def product(self, product: str):
        '''Setting up Sentinel 2 product file.

        Parameters
        ----------
        product : str

        Raises
        ----------
        InvalidProductError
        '''
        if not isinstance(product, str):
            raise InvalidProductError(
                feature='Product', value=product, message=f'Product must be a string not an {product.__class__.__qualname__}.')
        if not Path(product).exists():
            raise InvalidProductError(
                feature='Product', value=product, message=f'No file named {product}.')
        if zipfile.is_zipfile(product):
            raise InvalidProductError(
                feature='Product', value=product, message='Product must be unzipped!')
        self._product = product

    @property
    def product_type(self) -> str:
        return self._product_type

    @product_type.setter
    def product_type(self, p_type: str) -> None:
        '''Setting up Sentinel 2 product type.

        Parameters
        ----------
        p_type : str

        Raises
        ----------
        InvalidProductTypeError
        '''
        if p_type is not None:
            if not isinstance(p_type, str) or p_type.upper() not in ('L1C', 'L2A'):
                raise InvalidProductTypeError(
                    feature='Product type', value=p_type, message='Invalid product type value. Possible options are: "L1C" or "L2A"')
            self._product_type = p_type.upper()
        else:
            self._infer_product_type(p_type)

    def _infer_product_type(self, p_type: str) -> None:
        '''Infers product type from product name

        Parameters
        ----------
        p_type : str

        Raises
        ----------
        InvalidProductTypeError
        '''

        if 'MSIL1C' in str(self.product.upper()):
            self.product_type = 'L1C'
        elif 'MSIL2A' in str(self.product.upper()):
            self.product_type = 'L2A'
        else:
            raise InvalidProductTypeError(
                feature='Product type', value=p_type, message='Product type must be set. Possible options are: "L1C" or "L2A"')

    def setup_bands(self) -> None:
        '''Method for setting up band file paths.

        '''

        bands = BandsFactory().get_product_bands(self.product, self.product_type)
        bands.set_bands()
        bands.validate_bands()
        self.bands = bands.get_bands()

        self._set_up_steps['Bands setup'] = True

    def resample_swir_to_10m(self) -> None:
        '''Method for resampling and saving swir 1 and 2 bands.'''

        # Creates directory in current working directory
        create_dir('_resampled')

        # File paths where resampled swir rasters will be saved
        swir_resampled_files = get_resampled_swir_files(self.product)

        # 10m raster used as target for resampling and reading metadata
        blue_10m = self.bands['10m']['blue']

        for swir, file in swir_resampled_files.items():
            # Check if swir band is already resampled
            if not file.resolve().exists():
                swir_to_resample = ResampledRaster(
                    raster_to_resample=self.bands['20m'][swir], target_raster=blue_10m)
                # 10m resampled raster as numpy array
                swir_resampled = swir_to_resample.get_resampled_raster()

                # Saving as .gtif image in ./_resampled folder
                save_raster_image(input_raster=swir_resampled,
                                  output_file=file, meta=swir_to_resample.meta)

        # Setting file paths for resampled rasters
        self.bands['10m']['swir_1'] = str(Path(swir_resampled_files['swir_1']))
        self.bands['10m']['swir_2'] = str(Path(swir_resampled_files['swir_2']))

        self._set_up_steps['Swir resampling'] = True

    def calculate_spectral_indices(self) -> None:
        '''Method for calculating necessary spectral indices.
        Necessary indices are:  AWEI - automated water extraction index
                                NDVI - normalized difference vegetation index
                                BAEI - built-up area extraction index
                                NDTI - normalized difference tillage index

        '''

        if self._set_up_steps['Swir resampling'] != True:
            raise BandNotResampledError(
                feature='swir_1 or swir_2', value='None', message='SWIR bands must be resampled to 10m before calculating spectral indices')

        # Creates directory in current working directory
        create_dir('_spec_index')

        # Dict with file paths where spectral index rasters will be saved
        spec_index_files = get_spectral_index_files(self.product)

        spectral_index_factory = SpectralIndexFactory()

        for spec_index_name, file in spec_index_files.items():
            if not file.resolve().exists():
                # Create spectral index
                spec_index = spectral_index_factory.get_spectral_index(
                    spec_index=spec_index_name, bands=self.bands['10m'])
                # Spectral index as numpy array
                spec_index_calculated = spec_index.calculate_index()
                # No data value for calculated spectral index
                no_data_value = get_spectral_index_no_data_values()[
                    spec_index_name]
                # Spectral index with masked no data values
                spec_index_no_data_masked = set_no_data_to_99999(
                    spec_index=spec_index_calculated, no_data=no_data_value)

                # Saving as .gtif image in ./_spec_index folder
                save_raster_image(input_raster=spec_index_no_data_masked,
                                  output_file=file, meta=spec_index.meta)

        # Setting file paths for spectral indices
        self.spectral_index['awei'] = str(Path(spec_index_files['AWEI']))
        self.spectral_index['ndvi'] = str(Path(spec_index_files['NDVI']))
        self.spectral_index['baei'] = str(Path(spec_index_files['BAEI']))
        self.spectral_index['ndti'] = str(Path(spec_index_files['NDTI']))

        self._set_up_steps['Spectral indices calculation'] = True