# program.py
from abc import ABC
from typing import Any, List
from qilimanjaroq_server.algorithm.algorithm_manager import AlgorithmManager
from qilimanjaroq_server.algorithm.bellstate_algorithm_manager import BellStateAlgorithmManager
from qilimanjaroq_server.typings.algorithm import ProgramDefinition, AlgorithmDefinition, AlgorithmName
from qilimanjaroq_server.typings.job import JobBackend


class Program(ABC):
    """ class to handle a program execution that may include a collection of Algorithms

    """

    def __init__(self, program_definition: ProgramDefinition) -> None:
        algorithm_definitions = [algorithm_definition for algorithm_definition in program_definition.algorithms]
        self._algorithm_managers = [
            self._create_specific_algorithm(algorithm_definition=algorithm_definition) for algorithm_definition in algorithm_definitions]

    def _create_specific_algorithm(self, algorithm_definition: AlgorithmDefinition) -> AlgorithmManager:
        """ from a given algorithm definition, creates the corresponding algorithm manager

        Args:
            algorithm_definition (AlgorithmDefinition): Algorithm definition structure

        Returns:
            AlgorithmManager: algorithm manager
        """
        print(f'Algorithm Definition type: {type(algorithm_definition)}')
        if algorithm_definition.name == AlgorithmName.BELLSTATE.value:
            return BellStateAlgorithmManager(options=algorithm_definition.options)

        raise ValueError(f"Algorithm not supported: {algorithm_definition.name}")

    def execute(self, backend: JobBackend) -> List[Any]:
        """ Executes the program running all algorithms defined

        Returns:
            Any: The program execution result
        """
        return [algorithm_manager.execute(backend=backend) for algorithm_manager in self._algorithm_managers]
