import numpy as np
from actomyosin_analyser.model.bead_states import BeadStates


def test_get_indices_of_filament():
    links_array = np.full((30, 3), -1, dtype=int)
    links_array[4, 1] = 12
    links_array[12, 0] = 4
    links_array[9, 1] = 7
    links_array[7, 0] = 9
    links_array[7, 1] = 14
    links_array[14, 0] = 7
    links_array[14, 1] = 8
    links_array[8, 0] = 14

    bead_states = BeadStates(links_array.flatten())

    indices_f0 = bead_states.get_indices_of_filament(0)
    assert(2 == len(indices_f0))
