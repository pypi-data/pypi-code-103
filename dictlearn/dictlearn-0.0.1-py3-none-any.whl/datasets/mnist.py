from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from ..utils.data_utils import get_file


def load_data(path='mnist.npz'):
    """
    Loads the MNIST dataset

    Arguments:
        path: path where to cache the dataset locally
              (relative to ~/.dl/datasets)

    Returns:
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`

    Example::

        (X_train, y_train), (X_test, y_test) = mnist.load_data()
    """
    path = get_file(
        path,
        origin='https://dl-databases.s3-eu-west-1.amazonaws.com/mnist.npz',
        file_hash='8a61469f7ea1b51cbae51d4f78837e45'
    )
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']
        f.close()
    return (x_train, y_train), (x_test, y_test)
