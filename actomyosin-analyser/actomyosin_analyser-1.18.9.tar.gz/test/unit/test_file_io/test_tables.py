import pandas as pd
import numpy as np
from actomyosin_analyser.file_io.tables import _remove_floats_where_isclose


def test_remove_floats_where_isclose():

    x = np.linspace(0, 1, 7)
    y = np.ones(7, dtype=int)
    index1 = pd.MultiIndex.from_arrays(
        [x, y],
        names=['x', 'y']
    )

    x_diff = x[:]
    x_diff[5:] += 0.000001
    index2 = pd.MultiIndex.from_arrays(
        [x_diff, y],
        names=['x', 'y']
    )
    diff_index = index2.difference(index1)
    assert 2 == len(diff_index)

    diff_after_removal = _remove_floats_where_isclose(diff_index, index1)
    assert 0 == len(diff_after_removal)