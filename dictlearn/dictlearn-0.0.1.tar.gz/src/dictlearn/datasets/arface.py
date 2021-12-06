from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from ..utils.data_utils import get_file


def load_data(path='arface.npz'):
    """
    Loads the AR Face dataset

    Arguments:
        path: path where to cache the dataset locally
              (relative to ~/.dl/datasets)

    Returns:
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`

    Example::

        (X_train, y_train), (X_test, y_test) = arface.load_data()
    """
    path = get_file(
        path,
        origin='https://dl-databases.s3-eu-west-1.amazonaws.com/arface.npz',
        file_hash='0f0501fd435873b9d3228da47d772af2'
    )
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
        f.close()
    return (x_train, y_train), (x_test, y_test)
