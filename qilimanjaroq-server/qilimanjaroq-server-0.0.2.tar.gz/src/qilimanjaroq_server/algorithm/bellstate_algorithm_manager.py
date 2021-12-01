# bellstate_job_manager.py
from qilimanjaroq_server.typings.algorithm import AlgorithmOptions
from qilimanjaroq_server.typings.job import JobBackend
from .algorithm_manager import AlgorithmManager
from qilimanjaroq_server.algorithm.algorithm import Algorithm
from qilimanjaroq_server.algorithm.bellstate import BellState


class BellStateAlgorithmManager(AlgorithmManager):
    """ concrete class to implement a bell state job manager
        to create a BellState Algorithm class and 
        manage its algoritm function
    """

    def factory_method(self, backend: JobBackend) -> Algorithm:
        return BellState(options=self._options, backend=backend)
