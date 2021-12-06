"""Exception modeule"""


class InvalidPipelineId(Exception):
    """Invalid pipeline id format."""


class NonActiveModelTrackingID(Exception):
    """A non-active model tracking ID was provided.
    """


class NotofTypeDictionary(Exception):
    """A dictionary is expected.
    """


class NoConfig(Exception):
    """No configuration file was found or provided
    """


class InvalidComputeResource(Exception):
    """Invalid compute resource provided.
    """


class InvalidEstimator(Exception):
    """ Invalid ac type provided. Available Sagemaker Estimators are sklearn and tensorflow.
                """


class LengthMismatch(Exception):
    """ Invalid length
                """


class NotDataFrame(Exception):
    """ Data is not a pandas DataFrame
                """


class NotofTypeArray(Exception):
    """ Data is not of type np.ndarray
                """


class NotofTypeInt(Exception):
    """Variable must be of type int"""


class NotofTypeList(Exception):
    """Variable must be of type list"""
