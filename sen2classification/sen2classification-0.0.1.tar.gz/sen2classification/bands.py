from pathlib import Path

from .exceptions import MissingNecessaryBandError


# L1C bands by resolution, different form L2A
RESOLUTION_L1C = {
    '10m': ['blue', 'green', 'red', 'nir'],
    '20m': ['red_edge_1', 'red_edge_2', 'red_edge_3', 'red_edge_8a', 'swir_1', 'swir_2'],
    '60m': ['aerosol', 'water_vapour', 'cirrus']
}

# Bands necessary for calculating spectral indices and preforming classification
NECESSARY_10M_BANDS = ['blue', 'green', 'red', 'nir']
NECESSARY_20M_BANDS = ['swir_1', 'swir_2']


class Bands:
    '''Class for finding Sentinel 2 band file paths.

    Attributes
    ----------
    product : str
        sentinel 2 product
    product_type : str
        sentinel 2 product type
    bands : dict
        dictionary containing band file paths 

    Methods
    -------
    get_bands()

    validate_bands()

    '''

    def __init__(self, product: str, product_type: str) -> None:
        '''Creates bands instance with empty bands dict.

        Parameters
        ----------

        product : str

        product_type: str

        '''
        self.product = product
        self.product_type = product_type
        self.bands: dict = {
            '10m': {},
            '20m': {},
            '60m': {}
        }

    def get_bands(self) -> dict:
        """Returns dictionary containing band file paths.

        Returns
        ----------
        dict

        """
        return self.bands

    def set_bands(self) -> None:
        pass

    def validate_bands(self) -> None:
        '''Validate bands that are necessary for classification.

        Raises
        ----------
        MissingNecessaryBandError

        '''

        for band_10m in NECESSARY_10M_BANDS:
            if band_10m not in self.bands['10m']:
                raise MissingNecessaryBandError(feature=band_10m.upper(
                ), value='None', message=f'{band_10m.upper()} band not found in Sentinel 2 {self.product_type} product! Cannot preform classification. Check if product is corrupt and try to download it again.')
        for band_20m in NECESSARY_20M_BANDS:
            if band_20m not in self.bands['20m']:
                raise MissingNecessaryBandError(feature=band_20m.upper(
                ), value='None', message=f'{band_20m.upper()} band not found in Sentinel 2 {self.product_type} product! Cannot preform classification. Check if product is corrupt and try to download it again.')


class L1CBands(Bands):
    '''Class for finding Sentinel 2 L1C band file paths.

    Methods
    -------
    set_bands()

    '''

    def __init__(self, product: str, product_type: str) -> None:
        super().__init__(product, product_type)

    def set_bands(self) -> None:
        '''Method for navigating L1C product directory structure'''

        all_bands = find_bands(Path(self.product))

        for band_name, band_path in all_bands.items():
            if band_name in RESOLUTION_L1C['10m']:
                self.bands['10m'][band_name] = band_path
            elif band_name in RESOLUTION_L1C['20m']:
                self.bands['20m'][band_name] = band_path
            elif band_name in RESOLUTION_L1C['60m']:
                self.bands['60m'][band_name] = band_path


class L2ABands(Bands):
    '''Class for finding Sentinel 2 L2A band file paths.

    Methods
    -------
    set_bands()
    
    '''

    def __init__(self, product: str, product_type: str) -> None:
        super().__init__(product, product_type)

    def set_bands(self) -> None:
        '''Method for navigating L2A product directory structure'''

        for dir in Path(self.product).rglob('*'):
            if dir.name == 'R10m':
                self.bands['10m'] = find_bands(dir)
            elif dir.name == 'R20m':
                self.bands['20m'] = find_bands(dir)
            elif dir.name == 'R60m':
                self.bands['60m'] = find_bands(dir)


class BandsFactory:
    '''Factory for creating Bands objects.

    Methods
    -------
    get_product_bands(product, product_type)
        returns bands object
    '''

    def get_product_bands(self, product: str, product_type: str) -> Bands:
        '''Returns Bands object based on product type.

        Parameters
        ----------
        product : str

        product_type: str

        Returns:
        ----------
        Bands
        '''
        if product_type == 'L1C':
            return L1CBands(product, product_type)
        elif product_type == 'L2A':
            return L2ABands(product, product_type)


def find_bands(dir: Path) -> dict:
    ''' Helper method for finding band files in a directory.

    Returns
    ----------
    dict
    '''

    bands_file_path = {}
    for file_path in dir.rglob('*'):
        file_path_str = str(file_path)
        if file_path_str.endswith('.jp2'):
            if 'AOT' in file_path_str:
                bands_file_path['aot'] = file_path_str
            elif 'B01' in file_path_str:
                bands_file_path['aerosol'] = file_path_str
            elif 'B02' in file_path_str:
                bands_file_path['blue'] = file_path_str
            elif 'B03' in file_path_str:
                bands_file_path['green'] = file_path_str
            elif 'B04' in file_path_str:
                bands_file_path['red'] = file_path_str
            elif 'B05' in file_path_str:
                bands_file_path['red_edge_1'] = file_path_str
            elif 'B06' in file_path_str:
                bands_file_path['red_edge_2'] = file_path_str
            elif 'B07' in file_path_str:
                bands_file_path['red_edge_3'] = file_path_str
            elif 'B08' in file_path_str:
                bands_file_path['nir'] = file_path_str
            elif 'B8A' in file_path_str:
                bands_file_path['red_edge_8a'] = file_path_str
            elif 'B09' in file_path_str:
                bands_file_path['water_vapour'] = file_path_str
            elif 'B10' in file_path_str:
                bands_file_path['cirrus'] = file_path_str
            elif 'B11' in file_path_str:
                bands_file_path['swir_1'] = file_path_str
            elif 'B12' in file_path_str:
                bands_file_path['swir_2'] = file_path_str
            elif 'SCL' in file_path_str:
                bands_file_path['scl'] = file_path_str
            elif 'TCI' in file_path_str:
                bands_file_path['rgb'] = file_path_str
            elif 'WVP' in file_path_str:
                bands_file_path['wvp'] = file_path_str

    return bands_file_path
