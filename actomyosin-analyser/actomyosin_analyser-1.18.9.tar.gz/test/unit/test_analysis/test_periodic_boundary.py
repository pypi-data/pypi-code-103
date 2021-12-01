import numpy as np
from actomyosin_analyser.analysis.periodic_boundaries import revert_minimum_image_projection

def test_revert_minimum_image_projection():
    box = np.ones(3) * 10

    # ===============================================================================
    # particle 1 crosses x-border once, particle 2 crosses x-border and y-border once
    pos_particle_1 = np.ones((10, 3)) * 5
    pos_particle_1[:5, 0] += np.arange(5)
    pos_particle_1[5:, 0] = np.arange(5)
    pos_particle_2 = pos_particle_1.copy()
    pos_particle_2[:5, 1] -= np.arange(5)
    pos_particle_2[5:, 1] = 10 - np.arange(5)

    positions = np.empty((10, 2, 3))
    positions[:, 0] = pos_particle_1
    positions[:, 1] = pos_particle_2

    real_positions = revert_minimum_image_projection(positions, box)

    assert (real_positions[:, 0, 0] == np.arange(10) + 5).all()
    assert (real_positions[:, 0, 1:] == positions[:, 0, 1:]).all()
    assert (real_positions[:, 1, 0] == np.arange(10) + 5).all()
    assert (real_positions[:, 1, 1] == 5 - np.arange(10)).all()
    assert (real_positions[:, 1, 2] == positions[:, 1, 2]).all()

    # ==================================================================
    # particle 1 crosses x-border 2 times forward and one time backwards
    pos_particle_1 = np.ones((30, 3)) * 5
    pos_particle_1[:5, 0]   += np.arange(5)
    pos_particle_1[5:10, 0]  = np.arange(5)
    pos_particle_1[10:15, 0] = 5 + np.arange(5)
    pos_particle_1[15:20, 0] = np.arange(5)
    pos_particle_1[20:25, 0] = 5 - np.arange(5)
    pos_particle_1[25:, 0]   = 10 - np.arange(5)

    positions = np.empty((30, 1, 3))
    positions[:, 0, :] = pos_particle_1

    real_positions = revert_minimum_image_projection(positions, box)

    assert (real_positions[:, 0, 0] == np.concatenate([5 + np.arange(20), 25 - np.arange(10)])).all()
    assert (real_positions[:, 0, 1:] == positions[:, 0, 1:]).all()


