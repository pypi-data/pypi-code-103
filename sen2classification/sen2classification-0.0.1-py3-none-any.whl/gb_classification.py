from typing import Callable
from typing import Tuple
from collections import Counter

import numpy as np
import xgboost
from xgboost import DMatrix
from xgboost import train
from imblearn.over_sampling import SMOTE

from .product import Sentinel2Product
from .metas import ResampledMeta
from .metas import LandCoverMeta
from .helpers import read_raster_image
from .helpers import get_nodata_values
from .helpers import save_raster_image
from .helpers import get_classification_raster_file
from .helpers import get_label_raster_file
from .helpers import run_cleanup
from .land_cover_classification import LandCoverTresholdFactory
from .exceptions import SetupNotCompletedError


class GBClassification(Sentinel2Product):
    '''Class for classifying Sentinel 2 land cover using gradient boost algorithm.
    Gradient boost classification algorithm is used for solving supervised classification problems. 
    GBClassification automatically collects training data samples for each land cover class by tresholding spectral indices.
    If land cover class training data distribution is imbalanced, oversampling is used to balance the data.

    Sentinel 2 L1C and L2A product can be used as inputs. Clouds are not classified, for best results images with low cloud coverage should be used.

    Before running algorithm, basic setup must be completed.

    Bands must be set up -> setup_bands()

    Swir bands must be resampled from 20m to 10m resolution -> resample_swir_to_10m()

    Spectral indices that are used for classification (AWEI, NDVI, NDTI, BAEI) must be calculated -> calculate_spectral_indices()

    Final XGB classification raster is saved in current working directory.
    Example of use:

        xgb = GBClassification(product='test\data\S2B_MSIL1C_20210902T100029_N0301_R122_T33TVK_20210902T121054.SAFE', product_type='L1C')

        xgb.setup_bands()

        xgb.resample_swir_to_10m()

        xgb.calculate_spectral_indices()

        xgb.run()

    Attributes
    ----------
    product : str
        sentinel 2 product file path
    product_type : str
        sentinel 2 product type ("L1C" or "L2A")

    Methods
    -------
    run(cleanup = True)
        runs gradient boost classification algorithm. To keep all intermediate rasters created during classification, i.e. spectral indices, set cleanup to false.
        Defaults to True.
    '''

    def __init__(self, product: str, product_type: str = None) -> None:
        super().__init__(product, product_type)
        self._classification_raster = get_classification_raster_file(
            self.product, 'XGB')

    def _create_empty_raster(self) -> np.ndarray:
        '''Creates empty raster with all values set to 0.

        Returns
        ----------
        numpy array
        '''

        meta = ResampledMeta(self.bands['10m']['blue']).get_meta()

        empty_raster = np.full(
            shape=(meta['height'], meta['width']), fill_value=0, dtype=np.uint8)

        return empty_raster

    def _treshold_labeling(self, raster: np.ndarray, land_cover_name: str, spec_index: str) -> np.ndarray:
        '''Labels pixels with land cover class (1-5). Class labels for each each pixel are determined by tresholding spectral indices.
        Class labels are:
            1: water
            2: low vegetation
            3: high vegetation
            4: soil
            5: built up

        Parameters
        ----------
        raster: numpy array
            empty raster or raster containing previously labeled pixels

        land_cover_name: str

        spec_index : str

        Returns
        ----------
        numpy array
        '''

        land_cover = LandCoverTresholdFactory().get_land_cover(
            land_cover=land_cover_name, product=self.product)
        spec_index = read_raster_image(self.spectral_index[spec_index])
        land_cover_classified = land_cover.treshold_classification(spec_index)
        # Label for land cover class (1-5)
        land_cover_label = np.unique(land_cover_classified)[-1]

        label_raster = np.where((land_cover_classified == land_cover_label) & (
            raster == 0), land_cover_classified, raster)
        return label_raster

    def _label_no_data(self, empty_raster: np.ndarray) -> np.ndarray:
        '''Labels no data values with value 6.

        Parameters
        ----------
        empty_raster: numpy array
            empty raster with all values set to 0

        Returns
        ----------
        numpy array

        '''

        # Value 0 represents no data value
        no_data_raster = get_nodata_values(self.bands['10m']['blue'])
        raster_no_data_label = np.where(no_data_raster == 0, 6, empty_raster)

        return raster_no_data_label

    def _create_label_raster(self) -> np.ndarray:
        '''Creates labels raster containing labeled pixel for each land cover class.
        It is used for taking training samples for gradient boost classification.

        Label raster is saved in current working directory as ./label_raster.tif

        Returns
        ----------
        numpy array

        '''

        label_raster_file = get_label_raster_file(self.product)

        if label_raster_file.exists():
            label_raster = read_raster_image(label_raster_file)
        else:
            empty_raster = self._create_empty_raster()
            raster_no_data_labeled = self._label_no_data(empty_raster)
            treshold_labeling_args = get_treshold_labeling_args()

            label_raster = self._pipe(
                raster_no_data_labeled, self._treshold_labeling, treshold_labeling_args)

            meta = LandCoverMeta(self.bands['10m']['blue']).get_meta()
            save_raster_image(label_raster, label_raster_file, meta)

        return label_raster

    def _pipe(self, label_raster: np.ndarray, tresh_func: Callable, tresh_func_args: tuple) -> np.ndarray:
        '''Pipe workflow used for creating label raster that contains all land cover class labels.
        Method _treshold_labeling is used for labeling every land cover class. Input raster for each iteration is previously labeled raster.

        Parameters
        ----------
        label_raster: numpy array

        tresh_func: function
            method _treshold_labeling
        tresh_func_args : tuple
            arguments for _treshold_labeling method


        Returns
        ----------
        numpy array
        '''
        for func_args in tresh_func_args:
            label_raster = tresh_func(
                label_raster, func_args['land_cover_name'], func_args['spec_index'])
        return label_raster

    def _collect_train_data(self, label_raster: np.ndarray, label: int) -> np.ndarray:
        '''Collects training data (pixels) for each land cover class. 5% of total pixel count, from each class, is selected for training.
        If training pixel count goes over 100 000, then only first 100 000 pixels are selected.

        Parameters
        ----------
        label_raster: numpy array

        label: int
            land cover class label

        Returns
        ----------
        numpy array
        '''

        land_cover = np.where(label_raster == label)[0]
        # Select 5% of land cover pixels for training
        land_cover_train_data = land_cover[:int(land_cover.shape[0]*0.05)]
        # Limit pixel count used for training to 100_000
        if land_cover_train_data.shape[0] > 100_000:
            land_cover_train_data = land_cover[:100_000]

        return land_cover_train_data

    def _create_train_labels(self, label_raster: np.ndarray) -> np.ndarray:
        '''Creates 1D array as a subset of label raster, containing only pixels used for training the model.

        Parameters
        ----------
        label_raster: numpy array


        Returns
        ----------
        numpy array
        '''
        label_raster_1D = label_raster.ravel()
        train_labels = self._create_empty_raster().ravel()

        for label in np.unique(label_raster):
            # Ignore non classified pixels
            if label == 0:
                continue
            land_cover_train_data = self._collect_train_data(
                label_raster_1D, label)
            train_labels[land_cover_train_data] = label

        return train_labels

    def _select_train_pixel_idx(self, train_labels: np.ndarray) -> np.ndarray:
        '''Selects pixel indices from train labels array that are used for training the model 
        i.e. all indices of pixels that are not 0 

        Parameters
        ----------
        train_labels: numpy array


        Returns
        ----------
        numpy array
        '''

        train_pixels_idx = np.flatnonzero(train_labels)

        return train_pixels_idx

    def _create_train_dataset(self, label_raster: np.ndarray, feature_raster: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        '''Creates array containing training features (X_train) and array containing training labels (y_train).

        Parameters
        ----------
        label_raster: numpy array

        feature_raster: numpy array

        Returns
        ----------
        tuple of numpy arrays

        '''

        train_labels = self._create_train_labels(label_raster)
        train_pixels_idx = self._select_train_pixel_idx(train_labels)

        X_train = feature_raster[train_pixels_idx]
        y_train = train_labels[train_pixels_idx]

        return X_train, y_train

    def _oversample(self, X_train: np.ndarray, y_train: np.ndarray, sampling_strategy: dict) -> Tuple[np.ndarray, np.ndarray]:
        '''Oversamples minority class(es). Minority class(es) are oversampled to have 70% the number of training data of the majority class.

        Parameters
        ----------
        X_train: numpy array

        y_train: numpy array

        sampling_strategy: dict

        Returns
        ----------
        tuple of numpy arrays
        '''

        oversample = SMOTE(sampling_strategy=sampling_strategy)

        X_train, y_train = oversample.fit_resample(X_train, y_train)

        return X_train, y_train

    def _balance_classes(self, X_train: np.ndarray, y_train: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        '''Balances classes by oversampling minority class(es).

        Parameters
        ----------
        X_train: numpy array

        y_train: numpy array

        Returns
        ----------
        tuple of numpy arrays

        '''
        counter = count_class_samples(y_train)
        sampling_strategy = create_sampling_strategy(counter)
        X_train_balanced, y_train_balanced = self._oversample(
            X_train, y_train, sampling_strategy)

        return X_train_balanced, y_train_balanced

    def _train_xgb_model(self, X: np.ndarray, y: np.ndarray) -> xgboost.Booster:
        '''Trains gradient boost model.

        Parameters
        ----------
        X: numpy array
            features

        y: numpy array
            labels

        Returns
        ----------
        xgboost.Booster
            trained model
        '''
        data_matrix = DMatrix(data=X, label=y)
        params = {'objective': 'multi:softmax', 'num_class': 7,
                  'max_depth': 5, 'tree_method': 'exact'}

        model = train(params, data_matrix, num_boost_round=8)

        return model

    def _predict(self, model: xgboost.Booster, feature_raster: np.ndarray) -> np.ndarray:
        '''Classifies all pixels of an image.

        Parameters
        ----------
        model: xgboost.Booster
            trained xgb model

        feature_raster: numpy array
            multiband raster

        Returns
        ----------
        1D numpy array
            classification raster
        '''
        classification = model.predict(DMatrix(feature_raster))

        return classification.astype('int8')

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
                    feature=step, value='False', message=f'{step} not completed. Before running GB algorithm setup methods must be called first : setup_bands -> resample_swir_to_10m -> calculate_spectral_indices.')

        # Multiband raster containing 6 spectral bands
        multiband_raster = create_multiband_raster(self.bands)
        # Reshaped as (row * col, num of bands)
        multiband_raster_1D = multiband_raster.reshape(
            (-1, multiband_raster.shape[2]))

        meta = LandCoverMeta(self.bands['10m']['blue']).get_meta()

        label_raster = self._create_label_raster()

        X_train, y_train = self._create_train_dataset(
            label_raster, multiband_raster_1D)

        X_train_balanced, y_train_balanced = self._balance_classes(
            X_train, y_train)

        model = self._train_xgb_model(X_train_balanced, y_train_balanced)

        xgb_classification_1D = self._predict(model, multiband_raster_1D)

        xgb_classification_2D = xgb_classification_1D.reshape(
            1, meta['height'], meta['width'])

        # TODO No data label changed from 6 to 0
        xgb_classification_2D_reclassified = np.where(
            xgb_classification_2D == 6, 0, xgb_classification_2D)

        save_raster_image(xgb_classification_2D_reclassified,
                          self._classification_raster, meta)

        if cleanup:
            run_cleanup()


def create_multiband_raster(bands: dict) -> np.ndarray:
    '''Creates multiband raster from bands:
        blue, green, red, nir, swir1, swir2.

    Parameters
    ----------
    bands : dict

    Returns
    ----------
    6D numpy array

    '''

    bands_to_combine = ['blue', 'green', 'red', 'nir', 'swir_1', 'swir_2']

    for band in bands_to_combine:
        # First time create multiband raster as single 2D raster
        if band == 'blue':
            multiband = read_raster_image(bands['10m'][band], only_first=True)
        # After that stack rasters on top of multiband raster
        else:
            singleband = read_raster_image(bands['10m'][band], only_first=True)
            multiband = np.dstack(tup=[multiband, singleband])

    return multiband.astype('uint16')


def get_treshold_labeling_args() -> tuple:
    '''Returns arguments for GBClassification method _treshold_labeling().
    Used when piping _treshold_labeling method
    '''
    return (
        {
            'land_cover_name': 'Water',
            'spec_index': 'awei'
        },
        {
            'land_cover_name': 'High_Vegetation',
            'spec_index': 'ndvi'
        },
        {
            'land_cover_name': 'Low_Vegetation',
            'spec_index': 'ndvi'
        },
        {
            'land_cover_name': 'Built_up',
            'spec_index': 'baei'
        },
        {
            'land_cover_name': 'Soil',
            'spec_index': 'ndti'
        }
    )


def count_class_samples(y_train: np.ndarray) -> list:
    '''Counts number of training samples for each class, sorted by number of training samples.

    Parameters
    ----------
    y_train : numpy array

    Returns
    ----------
    list
    '''
    counter = Counter(y_train)
    counter_sorted = counter.most_common()

    return counter_sorted


def create_sampling_strategy(counter: list) -> dict:
    '''Creates sampling strategy for every class. If class/majority_class ratio is less then 70%, that class is oversampled.

    Parameters
    ----------
    counter: list

    Returns
    ----------
    dict
    '''

    majority_class = counter[0][0]
    majority_class_samples = counter[0][1]

    sampling_strategy = {majority_class: majority_class_samples}

    # Start from second biggest class
    for label, n_samples in counter[1:]:
        if n_samples/majority_class_samples < 0.7:
            sampling_strategy[label] = int(majority_class_samples * 0.7)
        else:
            sampling_strategy[label] = n_samples

    return sampling_strategy
