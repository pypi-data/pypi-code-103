import numpy as np
from numba.typed import List
from actomyosin_analyser.analysis.analyser import Analyser



def test_coordinates_to_bin_indices():

    coordinates = np.array([
        [1.2, 1.2, 3.1],
        [1.9, 3.1, 2.5],
        [3.5, 1.5, 4.7],
        [4.9, 3.6, 5.4]
    ])

    range_x = [0, 6]
    range_y = [0, 5]
    range_z = [0, 6]

    wx = 1
    wy = 1
    wz = 1

    bin_indices = Analyser._coordinates_to_bin_indices(coordinates,
                                                       range_x, wx,
                                                       range_y, wy,
                                                       range_z, wz)

    assert (bin_indices[0] == (1, 1, 3)).all()
    assert (bin_indices[1] == (1, 3, 2)).all()
    assert (bin_indices[2] == (3, 1, 4)).all()
    assert (bin_indices[3] == (4, 3, 5)).all()

    # shift to zero centered box
    box = np.array([6, 5, 6])
    coordinates = coordinates - box / 2

    range_x = [-3, 3]
    range_y = [-2.5, 2.5]
    range_z = [-3, 3]

    bin_indices = Analyser._coordinates_to_bin_indices(coordinates,
                                                       range_x, wx,
                                                       range_y, wy,
                                                       range_z, wz)

    assert (bin_indices[0] == (1, 1, 3)).all()
    assert (bin_indices[1] == (1, 3, 2)).all()
    assert (bin_indices[2] == (3, 1, 4)).all()
    assert (bin_indices[3] == (4, 3, 5)).all()


def test_get_voxel_mask():

    coordinates = np.array([
        [1.2, 1.2, 3.1],
        [1.9, 3.1, 2.5],
        [3.5, 1.5, 4.7],
        [4.9, 3.6, 5.4]
    ])

    range_x = [0, 6]
    range_y = [0, 5]
    range_z = [0, 6]

    wx = 1
    wy = 1
    wz = 1

    bin_indices = Analyser._coordinates_to_bin_indices(coordinates,
                                                       range_x, wx,
                                                       range_y, wy,
                                                       range_z, wz)

    grid_range = (np.ones(3)*2.1).astype(int)
    mask_000_2 = Analyser._get_voxel_mask(bin_indices, grid_range,
                                          (0, 0, 0), (6, 5, 6))

    print(mask_000_2)
    assert not mask_000_2[0]
    assert mask_000_2[1]
    assert not mask_000_2[2]
    assert mask_000_2[3]

    grid_range = np.zeros(3, dtype=int)
    mask_000_0 = Analyser._get_voxel_mask(bin_indices, grid_range,
                                          (0, 0, 0), (6, 5, 6))
    assert not mask_000_0.any()

    mask_113_0 = Analyser._get_voxel_mask(bin_indices, grid_range,
                                          (1, 1, 3), (6, 5, 6))
    assert mask_113_0[0]
    assert not mask_113_0[1:].any()

    grid_range = (np.ones(3) * 2.1).astype(int)
    mask_034_2 = Analyser._get_voxel_mask(bin_indices, grid_range,
                                          (0, 3, 4), (6, 5, 6))
    assert mask_034_2[0]
    assert mask_034_2[1]
    assert not mask_034_2[2]
    assert mask_034_2[3]

    mask_044_2 = Analyser._get_voxel_mask(bin_indices, grid_range,
                                          (0, 4, 4), (6, 5, 6))

    assert mask_044_2[0]
    assert mask_044_2[1]
    assert not mask_044_2[2]
    assert mask_044_2[3]

def test_parse_items_and_motors_arrays_to_filament_tuples():
    _invalid = np.iinfo('uint32').max
    # crate items array with 8 columns
    items = np.array([
        list(range(0, 5)) + [_invalid] * 3,
        list(range(5, 9)) + [_invalid] * 4,
        list(range(9, 17)),
        list(range(17, 19)) + [_invalid] * 6
    ], dtype='uint32')
    # create motors array with 3 columns
    motors = np.array([
        [2, 3, _invalid],
        [7, _invalid, _invalid],
        [10, 13, 15],
        [_invalid] * 3
    ], dtype='uint32')

    fil_tuples = Analyser._parse_items_and_motors_arrays_to_filament_tuples(items, motors)

    f_items, f_motors = fil_tuples[0]
    assert len(f_items) == 5
    assert len(f_motors) == 2
    assert (0, 1, 2, 3, 4) == tuple(f_items)
    assert (2, 3) == tuple(f_motors)

    f_items, f_motors = fil_tuples[1]
    assert len(f_items) == 4
    assert len(f_motors) == 1
    assert (5, 6, 7, 8) == tuple(f_items)
    assert (7,) == tuple(f_motors)

    f_items, f_motors = fil_tuples[2]
    assert len(f_items) == 8
    assert len(f_motors) == 3
    assert (9, 10, 11, 12, 13, 14, 15, 16) == tuple(f_items)
    assert (10, 13, 15) == tuple(f_motors)

    f_items, f_motors = fil_tuples[3]
    assert len(f_items) == 2
    assert len(f_motors) == 0
    assert (17, 18) == tuple(f_items)
    assert tuple() == tuple(f_motors)

def test_get_maximum_items_and_value_for_filaments():

    filaments = [
        ([0, 1, 2, 3, 4, 5], [2, 3]),
        ([5, 6, 7, 8], [7]),
        (list(range(9, 17)), [10, 13, 15]),
        ([17, 18], [])
    ]

    typed_fil = List()

    [typed_fil.append((np.array(t[0]).astype('uint32'),
                       np.array(t[1]).astype('uint32'))) for t in filaments]

    max_idx, max_items, max_motors = Analyser._get_maximum_items_and_value_for_filaments(typed_fil)

    assert 18 == max_idx
    assert 8 == max_items
    assert 3 == max_motors
