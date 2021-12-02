"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Unit test module for Q Fever Model.

"""


import unittest

from pandas.util.testing 				  import assert_frame_equal
from emulsion.examples.qfever.qfever_main import *

class SeedTest(unittest.TestCase):


    """Tests with the same seed"""


    def test_simulator(self):

        """Test simulator give same output with same seed."""

        seed_number = 10
        steps = 10

        simu_param = StateVarDict(steps=steps)
        simu_param.update(DEFAULT_PARAM)

        np.random.seed(seed_number)
        simu = Simulation(TargetAgentClass=QfeverHerd, model=EmulsionModel(filename=simu_param['model_path']), **simu_param)
        simu.run()

        counts_1 = simu.counts

        np.random.seed(seed_number)
        simu = Simulation(TargetAgentClass=QfeverHerd, model=EmulsionModel(filename=simu_param['model_path']), **simu_param)
        simu.run()

        assert_frame_equal(counts_1, simu.counts)

if __name__ == '__main__':
    unittest.main()