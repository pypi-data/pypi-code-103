"""
System Utilities
----------------
It is a core module of MAICA to provide base utilities of the framework.
"""


import torch


# maica.data_old.base.read_data_file
ERR_DATA_FILE_EXT = 'Only .xlsx and .csv extensions are available, but unknown file extension {} was given.'

# maica.data_old.util.impute
ERR_UNKNOWN_IMPUTE = 'Unknown imputation method {}.'

# maica.data_old.util.get_split_idx
ERR_INVALID_SPLIT_RATIO = 'Ratio must be in (0, 1), but the given ratio is {:.4f}'

# maica.data_old.vector.Vector.denormalize
ERR_UNNORMALIZED = 'The input data_old of this dataset has never been normalized.'

# maica.data_old.vector.load_dataset
ERR_EMPTY_FEAT_IDX = 'Indices of the input features must be provided to load the dataset object.'

# maica.data_old.formula.load_dataset
ERR_EMPTY_FORM_IDX = 'Indices of the chemical formulas must be provided to load the dataset object.'

# maica.data_old.molecule.load_dataset, maica.data_old.crystal.load_dataset
ERR_EMPTY_STRUCT_IDX = 'Indices of the structures must be provided to load the dataset object.'

# maica.util.optimization.run_ml_model
ERR_UNKNOWN_ALG = 'The type of the algorithm {} is unknown.'

# maica.ml_old.base.Model
ERR_UNKNOWN_PIPELINE = 'Unknown pipeline type {} was given.'


# Global configurations of machine learning algorithms.
run_gpu = False


def set_gpu_runnable(runnable: bool):
    """
    Set GPU enable for running machine learning algorithm in GPU.

    :param runnable: A flag to indicate the GPU enable.
    :return: None

    Example:

    >>> set_gpu_runnable(True) # Enable GPU.
    """

    if torch.cuda.is_available():
        global run_gpu
        run_gpu = runnable
    else:
        print('GPU is not available in your system. Make sure the CUDA Driver is installed in the system.')
