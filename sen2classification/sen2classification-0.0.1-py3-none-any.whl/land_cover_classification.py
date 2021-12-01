from typing import Tuple
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from rasterio.plot import reshape_as_image


from .metas import LandCoverMeta
from .metas import KmeansMeta
from .helpers import get_file_name
from .helpers import save_raster_image
from .helpers import read_raster_image
from .exceptions import LandCoverNotSeparatedError


class LandCover:
    '''Base class for land cover classification.

    Attributes
    ----------
    product_name : str
        sentinel 2 product name


    Methods
    -------
    get_meta(band_10m)
        returns LandCoverMeta


    '''

    def __init__(self, product: str) -> None:
        self.product_name = get_file_name(product)

    def get_meta(self, band_10m: str) -> dict:
        return LandCoverMeta(band_10m).get_meta()

    def is_classified(self):
        pass


class LandCoverTreshold(LandCover):
    '''Class for performing treshold classification.


    Methods
    -------

    is_classified()
        checks if land cover is classified

    '''

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''Land cover is classified by tresholding spectral index.

        Parameters
        ----------
        spec_index : numpy array


        Return
        ----------
        numpy array
        '''
        pass

    def get_land_cover_file(self) -> Path:
        pass

    def is_classified(self) -> bool:
        if self.get_land_cover_file().exists():
            return True
        return False


class WaterTreshold(LandCoverTreshold):
    '''Class for water treshold classification using AWEI spectral index.


    Methods
    -------
    treshold_classification(spec_index: np.ndarray)
        performs treshold classification

    get_land_cover_file(band_10m)
        returns land cover file


    '''

    def __init__(self, product: str) -> None:
        super().__init__(product)

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''Water is classified by tresholding AWEI.

        AWEI > -1000 = water

        '''
        water = np.where(((spec_index > -1000) & (spec_index != 99999)), 1, 0)
        return water

    def get_land_cover_file(self):
        return Path(f'_land_cover/water_{self.product_name}.tif')


class LowVegetationTreshold(LandCoverTreshold):
    '''Class for low vegetation treshold classification using NDVI spectral index.


    Methods
    -------
    treshold_classification(spec_index: np.ndarray)
        performs treshold classification

    get_land_cover_file(band_10m)
        returns land cover file

    '''

    def __init__(self, product: str) -> None:
        super().__init__(product)

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''Low vegetation is classified by tresholding NDVI.

        low vegetation = 0.3 <= NDVI < 0.6

        '''
        low_veg = np.where(((spec_index >= 0.3) & (spec_index < 0.6)), 2, 0)
        return low_veg

    def get_land_cover_file(self) -> Path:
        return Path(f'_land_cover/low_veg_{self.product_name}.tif')


class HighVegetationTreshold(LandCoverTreshold):
    '''Class for high vegetation treshold classification using NDVI spectral index.


    Methods
    -------
    treshold_classification(spec_index: np.ndarray)
        performs treshold classification

    get_land_cover_file(band_10m)
        returns land cover file

    '''

    def __init__(self, product: str) -> None:
        super().__init__(product)

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''High vegetation is classified by tresholding NDVI.

        high vegetation = NDVI >= 0.6

        '''
        high_veg = np.where(((spec_index < 1) & (spec_index >= 0.6)), 3, 0)
        return high_veg

    def get_land_cover_file(self) -> Path:
        return Path(f'_land_cover/high_veg_{self.product_name}.tif')


class SoilTreshold(LandCoverTreshold):
    '''Class for soil treshold classification using NDTI spectral index.


    Methods
    -------
    treshold_classification(spec_index: np.ndarray)
        performs treshold classification

    get_land_cover_file(band_10m)
        returns land cover file

    '''

    def __init__(self, product: str) -> None:
        super().__init__(product)

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''Soil is classified by tresholding NDTI.

        NDTI < 0 OR NDTI >= 0.12 = soil

        '''

        soil = np.where(
            ((spec_index < 1) & ((spec_index < 0) | (spec_index >= 0.12))), 4, 0)
        return soil

    def get_land_cover_file(self) -> Path:
        return Path(f'_land_cover/soil_1_{self.product_name}.tif')


class BuiltUpTreshold(LandCoverTreshold):
    '''Class for built up treshold classification using BAEI spectral index.


    Methods
    -------
    treshold_classification(spec_index: np.ndarray)
        performs treshold classification

    get_land_cover_file(band_10m)
        returns land cover file

    '''

    def __init__(self, product: str) -> None:
        super().__init__(product)

    def treshold_classification(self, spec_index: np.ndarray) -> np.ndarray:
        '''Built up is classified by tresholding BAEI.

        0.45 =< BAEI <= 0.55 = built up

        '''
        built_up = np.where(
            ((spec_index >= 0.45) & (spec_index <= 0.55)), 5, 0)
        return built_up

    def get_land_cover_file(self) -> Path:
        return Path(f'_land_cover/built_up_1_{self.product_name}.tif')


class LandCoverTresholdFactory():
    '''Creates factory for creating LandCoverTreshold instances.

    Methods
    -------
    get_land_cover(land_cover: str, product: str)
        returns LandCoverTreshold instance 
    '''

    def get_land_cover(self, land_cover: str, product: str) -> LandCoverTreshold:
        '''Returns LandCoverTreshold instances based on land_cover.

        Parameters
        ----------
        land_cover: str

        product: str

        Returns:
        ----------
        LandCoverTreshold
        '''
        if land_cover == 'Water':
            return WaterTreshold(product)
        elif land_cover == 'Low_Vegetation':
            return LowVegetationTreshold(product)
        elif land_cover == 'High_Vegetation':
            return HighVegetationTreshold(product)
        elif land_cover == 'Soil':
            return SoilTreshold(product)
        elif land_cover == 'Built_up':
            return BuiltUpTreshold(product)


class LandCoverKmeans(LandCover):
    '''Class for performing k-means classification.

    Methods
    -------

    get_k_means_meta(band_10m)
        return KmeansMeta

    k_means(spec_index_masked: np.ndarray, k: int)
        performs k means classification

    create_k_means_raster(spec_index_masked: np.ndarray)
        creates k means raster

    get_spec_index_k_class_medians(spec_index_masked: np.ndarray)
        calculates spectral index median value for each k means class 

    '''

    def __init__(self, product: str, band_10m: str) -> None:
        super().__init__(product)
        self.band_10m = band_10m

    def get_k_means_file(self) -> Path:
        pass

    def get_land_cover_file(self) -> dict:
        pass

    def get_k_means_meta(self, band_10m) -> dict:
        return KmeansMeta(band_10m).get_meta()

    def k_means(self, spec_index_masked: np.ndarray, k: int) -> np.ndarray:
        '''Performs K means classification in k classes. Returns 2D numpy array.

        Parameters
        ----------
        k : int
            Number of classes.

        Return
        ----------
        numpy array

        '''

        # Raster is reshaped to 1D = (row * col, 1)
        input_data = reshape_raster_for_classification(spec_index_masked)
        # Create model
        k_means_mini = MiniBatchKMeans(n_clusters=k)
        # Train model
        k_means_mini.fit(input_data)

        # Classification results
        classification_1D = k_means_mini.labels_
        classification_raster_2D = classification_1D.reshape(
            1, spec_index_masked.shape[1], spec_index_masked.shape[2]).astype('uint8')

        return classification_raster_2D

    def create_k_means_raster(self, spec_index_masked: np.ndarray):
        '''Creates k means classification raster.
        Raster is saved in ./_k_means/

        Parameters
        ----------
        spec_index_masked : numpy array
        '''

        # Performing kmeans classification and saving kmeans classification raster
        k_means_raster = self.k_means(spec_index_masked=spec_index_masked, k=4)
        k_meta = self.get_k_means_meta(self.band_10m)
        k_means_file = self.get_k_means_file()

        save_raster_image(k_means_raster, k_means_file, k_meta)

    def get_spec_index_k_class_medians(self, spec_index_masked: np.ndarray) -> list:
        '''Returns spectral index median value for each k means class.

        Parameters
        ----------
        spec_index_masked : numpy array

        Return
        ----------
        list
        '''

        k_means_file = self.get_k_means_file()

        if not k_means_file.exists():
            self.create_k_means_raster(spec_index_masked)

        k_medians = calculate_spec_index_k_class_medians(
            spec_index_masked=spec_index_masked, k_means_file=str(k_means_file))

        return k_medians

    def is_classified(self) -> bool:
        for file in self.get_land_cover_file().values():
            if not file.exists():
                return False
        return True

    def separate_land_covers(self, spec_index_masked: np.ndarray):
        pass


class VegetationKmeans(LandCoverKmeans):
    '''Class used for separating high and low vegetation using kmeans classification.

    Methods
    -------
    get_k_means_file()
        return file path for k-means raster

    get_land_cover_file()
        return file path for land cover

    separate_land_covers(self, spec_index_masked: np.ndarray)
        separates vegetation into high and low 
    '''

    def __init__(self, product: str, band_10m: str) -> None:
        super().__init__(product, band_10m)

    def get_k_means_file(self) -> Path:
        return Path(f'_k_means/ndvi_k4_{self.product_name}.tif')

    def get_land_cover_file(self) -> dict:
        return {
            'high_veg': Path(f'_land_cover/high_veg_{self.product_name}.tif'),
            'low_veg': Path(f'_land_cover/low_veg_{self.product_name}.tif')
        }

    def separate_land_covers(self, spec_index_masked: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        '''Vegetation is separated into high and low vegetation by extracting classes from k means classification.
        If k-means doesn't successfully separate high and low vegetation LandCoverNotSeparatedError is raised.

        Parameters
        ----------
        spec_index_masked : numpy array


        Return
        ----------
        tuple of numpy arrays

        Raises  
        ----------
        LandCoverNotSeparatedError

        '''

        k_medians = self.get_spec_index_k_class_medians(
            spec_index_masked)

        k_means_raster = read_raster_image(self.get_k_means_file())

        # K means successfully separated high and low vegetation
        if len(k_medians) == 3:
            # K means class with biggest median value = high vegetation
            high_veg_k_class = k_medians.pop()[0]
            high_veg = get_k_means_class_raster(
                k_means=k_means_raster, k_class=high_veg_k_class, raster_value=3)

            # K means class with second biggest median value = low vegetation
            low_veg_k_class = k_medians.pop()[0]
            low_veg = get_k_means_class_raster(
                k_means=k_means_raster, k_class=low_veg_k_class, raster_value=2)

            return high_veg, low_veg

        else:
            raise LandCoverNotSeparatedError()


class SoilBuiltUpKmeans(LandCoverKmeans):
    '''Class used for separating soil and built up using kmeans classification.

    Methods
    -------
    get_k_means_file()
        return file path for k-means raster

    get_land_cover_file()
        return file path for land cover

    separate_land_covers(self, spec_index_masked: np.ndarray)
        separates soil from built up 
    '''

    def __init__(self, product: str, band_10m: str) -> None:
        super().__init__(product, band_10m)

    def get_k_means_file(self) -> Path:
        return Path(f'_k_means/ndti_k4_{self.product_name}.tif')

    def get_land_cover_file(self) -> dict:
        return {
            'soil': Path(f'_land_cover/soil_2_{self.product_name}.tif'),
            'built_up': Path(f'_land_cover/built_up_2_{self.product_name}.tif')
        }

    def separate_land_covers(self, spec_index_masked: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        '''Soil and built up is separated by extracting classes from k means classification.
        If k-means doesn't successfully separate soil and built up LandCoverNotSeparatedError is raised.

        Parameters
        ----------
        spec_index_masked : numpy array


        Return
        ----------
        tuple of numpy arrays

        Raises  
        ----------
        LandCoverNotSeparatedError

        '''

        k_medians = self.get_spec_index_k_class_medians(
            spec_index_masked)

        k_means_raster = read_raster_image(self.get_k_means_file())

        # K means successfully separated soil and built up
        if len(k_medians) >= 2:

            # K means separated soil and built up into 3 classes
            if len(k_medians) == 3:
                # K means class with biggest and second biggest median value = soil
                soil_1_k_class = k_medians.pop()[0]
                soil_1 = get_k_means_class_raster(
                    k_means=k_means_raster, k_class=soil_1_k_class, raster_value=4)

                soil_2_k_class = k_medians.pop()[0]
                soil_2 = get_k_means_class_raster(
                    k_means=k_means_raster, k_class=soil_2_k_class, raster_value=4)

                soil = soil_1 + soil_2

                # K means class with lowest median value = built up
                built_up_k_class = k_medians.pop()[0]
                built_up = get_k_means_class_raster(
                    k_means=k_means_raster, k_class=built_up_k_class, raster_value=5)

            # K means separated soil and built up into 2 classes
            else:
                soil_k_class = k_medians.pop()[0]
                soil = get_k_means_class_raster(
                    k_means=k_means_raster, k_class=soil_k_class, raster_value=4)

                built_up_k_class = k_medians.pop()[0]
                built_up = get_k_means_class_raster(
                    k_means=k_means_raster, k_class=built_up_k_class, raster_value=5)

            return soil, built_up

        else:
            raise LandCoverNotSeparatedError()


class LandCoverKmeansFactory:
    '''Factory for creating LandCoverKmeans instances.

    Methods
    -------
    get_land_covers(land_cover: str, product: str)
        returns LandCoverKmeans instance 
    '''

    def get_land_covers(self, land_covers: str, product: str, band_10m: str) -> LandCoverKmeans:
        '''Returns LandCoverKmeans instances based on land_covers.

        Parameters
        ----------
        land_covers: str

        product: str

        band_10m: str

        Returns:
        ----------
        LandCoverKmeans
        '''
        if land_covers == 'Vegetation':
            return VegetationKmeans(product=product, band_10m=band_10m)
        elif land_covers == 'Soil_Built_up':
            return SoilBuiltUpKmeans(product=product, band_10m=band_10m)


def get_k_means_class_raster(k_means: np.ndarray, k_class: int, raster_value: int) -> np.ndarray:
    '''Returns k means class raster reclassified with given raster value.

    Parameters
    ----------
    k_means : numpy array

    k_class : int

    raster_value : int

    Return
    ----------
    numpy array

    '''

    k_means_class_raster = np.where(k_means == k_class, raster_value, 0)
    return k_means_class_raster


def calculate_spec_index_k_class_medians(spec_index_masked: np.ndarray, k_means_file: str) -> list:
    '''Calculates median spectral index value for each k means class.
    Returns list of tuples (k means class, spectral index median) sorted by median value.

    Parameters
    ----------
    spec_index_masked : numpy array

    k_means_file : str

    Return
    ----------
    dict
    '''

    k_means_raster = read_raster_image(k_means_file)

    # Key = k means class, value = masked spectral index median
    spec_index_medians = {}
    for k_means_class in np.unique(k_means_raster):
        # Spectral index masked with all others k means class except current one
        spec_index_masked_nan = np.where(
            k_means_raster == k_means_class, spec_index_masked, np.nan)
        # Median value for masked spectral index
        nan_median = np.nanmedian(spec_index_masked_nan)
        # Ignore masked pixels (with value 99999)
        if nan_median > 1:
            continue
        spec_index_medians[k_means_class] = nan_median

    # List of tuples (k means class, spec index median) sorted by median value
    return sorted(spec_index_medians.items(), key=lambda x: x[1])


def reshape_raster_for_classification(raster: np.ndarray) -> np.ndarray:
    '''Reshapes raster as 2D array suitable for K means classification. Returns 2D numpy array

    Parameters
    ----------
    raster : numpy array

    Return
    ----------
    numpy array

    '''

    raster_as_image = reshape_as_image(raster)
    raster_1D = raster_as_image.reshape(
        (-1, raster_as_image.shape[2]))

    return raster_1D
