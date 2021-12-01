import numpy as np

from .product import Sentinel2Product
from .exceptions import LandCoverNotSeparatedError
from .exceptions import SetupNotCompletedError
from .helpers import read_raster_image
from .helpers import save_raster_image
from .helpers import get_classification_raster_file
from .helpers import create_dir
from .helpers import run_cleanup
from .land_cover_classification import LandCoverTresholdFactory
from .land_cover_classification import LandCoverKmeansFactory


class ALCC(Sentinel2Product):
    '''Class for creating Automatic Land Cover Classification (ALCC) algorithm.
    Classification algorithm is based on spectral indices, which serve as an input for unsupervised classification algorithm - K means.
    K means unsupervised classification is used in combination with tresholding classification to create final land cover raster.

    Sentinel 2 L1C and L2A product can be used as inputs. Clouds are not classified, for best results images with low cloud coverage should be used.

    Before running algorithm, basic setup must be completed.

    Bands must be set up -> setup_bands()

    Swir bands must be resampled from 20m to 10m resolution -> resample_swir_to_10m()

    Spectral indices that are used for classification (AWEI, NDVI, NDTI, BAEI) must be calculated -> calculate_spectral_indices()

    Final ALCC classification raster is saved in current working directory.
    Example of use:

        alcc = ALCC(product='test\data\S2B_MSIL2A_20210902T100029_N0301_R122_T33TVK_20210902T121054.SAFE', product_type='L2A')

        alcc.setup_bands()

        alcc.resample_swir_to_10m()

        alcc.calculate_spectral_indices()

        alcc.run()


    Attributes
    ----------
    product : str
        sentinel 2 product file path
    product_type : str
        sentinel 2 product type ("L1C" or "L2A")

    Methods
    -------
    run(cleanup = True)
        runs ALCC algorithm. To keep all intermediate rasters created during classification, i.e spectral indices, set cleanup to false.
        Defaults to True.

    '''

    def __init__(self, product: str, product_type: str = None) -> None:
        '''Sentinel 2 alcc instance.

        Parameters
        ----------
        product : str

        product_type: str

        '''
        super().__init__(product, product_type)
        self._classification_raster = get_classification_raster_file(
            self.product, 'ALCC')

    def _remove_high_veg_from_water(self, water: np.ndarray) -> np.ndarray:
        '''Eliminates high vegetation from extracted water.

        Parameters
        ----------
        water : numpy array

        Returns
        ----------
        numpy array

        '''

        ndvi = read_raster_image(self.spectral_index['ndvi'])
        high_veg = LandCoverTresholdFactory().get_land_cover(
            land_cover='High_Vegetation', product=self.product)
        high_veg_classified = high_veg.treshold_classification(spec_index=ndvi)

        return np.where(high_veg_classified == 3, 0, water)

    def _tresholding(self, land_cover_name: str, spec_index_name: str) -> None:
        '''Land cover classification by tresholding spectral index.
        Values used for tresholding are predefined and static.

        Parameters
        ----------
        land_cover_name : str

        spec_index_name : str        
        '''

        land_cover = LandCoverTresholdFactory().get_land_cover(
            land_cover=land_cover_name, product=self.product)
        land_cover_file = land_cover.get_land_cover_file()

        if not land_cover.is_classified():
            # Spectral index used for classification
            spec_index = read_raster_image(
                self.spectral_index[spec_index_name])
            meta = land_cover.get_meta(self.bands['10m']['blue'])

            if land_cover_name == 'Water':
                water_classified = land_cover.treshold_classification(
                    spec_index)
                water_no_high_veg = self._remove_high_veg_from_water(
                    water_classified)
                # Save water raster as .gtif image in ./_land_cover folder
                save_raster_image(input_raster=water_no_high_veg,
                                  output_file=land_cover_file, meta=meta)
                # Creating alcc classification raster
                save_raster_image(input_raster=water_no_high_veg,
                                  output_file=self._classification_raster, meta=meta)
            else:
                alcc = read_raster_image(self._classification_raster)
                # Spectral index masked with alcc raster
                spec_index_masked = self._mask_spec_index_with_land_cover(
                    spec_index=spec_index, land_cover=alcc)
                land_cover_classified = land_cover.treshold_classification(
                    spec_index_masked)
                save_raster_image(input_raster=land_cover_classified,
                                  output_file=land_cover_file, meta=meta)

                alcc_updated = self._update_alcc_raster(
                    alcc=alcc, land_cover=land_cover_classified)
                save_raster_image(
                    alcc_updated, self._classification_raster, meta=meta)

    def _update_alcc_raster(self, alcc: np.ndarray, land_cover: np.ndarray) -> np.ndarray:
        '''Add classified land cover to alcc land cover classification raster

        Parameters
        ----------
        alcc : numpy array

        land_cover : numpy array

        Returns
        ----------
        numpy array
        '''

        return alcc + land_cover

    def _mask_spec_index_with_land_cover(self, spec_index: np.ndarray, land_cover: np.ndarray) -> np.ndarray:
        '''Mask spectral index raster with extracted land cover. Every land cover raster has only 2 values:
        0 - not land cover, (1,2,3,4,5) - land cover. 

        Parameters
        ----------
        spec_index : numpy array

        land_cover : numpy array

        Returns
        ----------
        numpy array

       '''

        masked_spec_index = np.where(land_cover == 0, spec_index, 99999)

        return masked_spec_index

    def _k_means_separation(self, land_covers_name: str, spec_index_name: str) -> None:
        '''Land covers are separated by kmeans classification. 
        K means is used to separate vegetation into high and low and to separate soil from built up.

        If k means separation of vegetation is unsuccessful, treshold classification is used to separate high and low vegetation.
        If k means separation of soil and built up is unsuccessful, the remaining pixels are classified as soil.

        Parameters
        ----------
        land_covers_name : str

        spec_index_name : str

        '''

        land_covers = LandCoverKmeansFactory().get_land_covers(land_covers=land_covers_name,
                                                               product=self.product, band_10m=self.bands['10m']['blue'])
        land_cover_file_1 = list(land_covers.get_land_cover_file().values())[0]
        land_cover_file_2 = list(land_covers.get_land_cover_file().values())[1]

        if not land_covers.is_classified():

            alcc = read_raster_image(self._classification_raster)
            spec_index = read_raster_image(
                self.spectral_index[spec_index_name])
            spec_index_masked = self._mask_spec_index_with_land_cover(
                spec_index=spec_index, land_cover=alcc)
            try:
                land_cover_1, land_cover_2 = land_covers.separate_land_covers(
                    spec_index_masked)

            except LandCoverNotSeparatedError:
                if land_covers_name == 'Vegetation':
                    low_vegetation = LandCoverTresholdFactory().get_land_cover(
                        land_cover='Low_Vegetation', product=self.product)
                    land_cover_1 = low_vegetation.treshold_classification(
                        spec_index_masked)

                    high_veg = LandCoverTresholdFactory().get_land_cover(
                        land_cover='High_Vegetation', product=self.product)
                    land_cover_2 = high_veg.treshold_classification(
                        spec_index=spec_index_masked)

                elif land_covers_name == 'Soil_Built_up':
                    # Remainig unclassified pixels are classified as soil
                    land_cover_1 = np.where(spec_index_masked == 99999, 0, 4)
                    land_cover_2 = None

            meta = land_covers.get_meta(self.bands['10m']['blue'])

            save_raster_image(land_cover_1, land_cover_file_1, meta)
            alcc_updated = self._update_alcc_raster(
                alcc=alcc, land_cover=land_cover_1)

            if land_cover_2 is not None:
                save_raster_image(land_cover_2, land_cover_file_2, meta)
                alcc_updated = self._update_alcc_raster(
                    alcc=alcc_updated, land_cover=land_cover_2)

            save_raster_image(
                alcc_updated, self._classification_raster, meta=meta)

    def run(self, cleanup: bool = True) -> None:
        '''Runs ALCC algorithm. If cleanup is set, all intermediate rasters created during classification are deleted.

        Parameters
        ----------
        cleanup: bool

        Raises  
        ----------
        SetupNotCompletedError

        '''

        for step, completed in self._set_up_steps.items():
            if not completed:
                raise SetupNotCompletedError(
                    feature=step, value='False', message=f'{step} not completed. Before running ALCC algorithm setup methods must be called first : setup_bands -> resample_swir_to_10m -> calculate_spectral_indices.')

        create_dir('_land_cover')
        create_dir('_k_means')

        self._tresholding(land_cover_name='Water', spec_index_name='awei')

        self._k_means_separation(
            land_covers_name='Vegetation', spec_index_name='ndvi')

        self._tresholding(land_cover_name='Soil', spec_index_name='ndti')

        self._tresholding(land_cover_name='Built_up', spec_index_name='baei')

        self._k_means_separation(
            land_covers_name='Soil_Built_up', spec_index_name='ndti')

        if cleanup:
            run_cleanup()
