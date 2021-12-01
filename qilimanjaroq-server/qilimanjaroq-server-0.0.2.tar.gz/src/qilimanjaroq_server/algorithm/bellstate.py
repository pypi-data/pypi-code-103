# bellstate_algorithm.py
from typeguard import typechecked
from qilimanjaroq_server.typings.algorithm import AlgorithmOptions, InitialValue
from qilimanjaroq_server.typings.job import JobBackend
from .algorithm import Algorithm
from qibo import gates
from qibo.models import Circuit
import numpy as np


class BellState(Algorithm):
    """ Class to handle a BellState algorithm."""

    @typechecked
    def __init__(self, options: AlgorithmOptions, backend: JobBackend) -> None:
        super().__init__(options=options, backend=backend)

        if backend is not backend.SIMULATOR:
            raise ValueError(
                f'Backend: {backend.value} is not supported. Only {backend.SIMULATOR.value} is currently supported.')
        self._create_bell_state_for_simulator_backend()

    def _create_bell_state_for_simulator_backend(self):
        number_qubits = self._options.number_qubits

        self._circuit = Circuit(number_qubits)
        self._circuit.add(gates.H(0))
        self._circuit.add(gates.CNOT(0, 1))
        self._initial_state = self._create_initial_state(number_qubits)

    def _create_initial_state(self, number_qubits: int):
        if self._options.initial_value == InitialValue.ZERO:
            return np.array([1.0] + [0.0] * (2**number_qubits - 1))
        if self._options.initial_value == InitialValue.ONE:
            return np.ones(2**number_qubits) / np.sqrt(2**number_qubits)
        if self._options.initial_value == InitialValue.RANDOM:
            value = np.random.rand(2**number_qubits)
            return value / np.linalg.norm(value)
        raise ValueError(f'Initial value: {self._options.initial_value} not supported.')

    @typechecked
    def execute(self) -> np.ndarray:
        if self._circuit is None or self._initial_state is None:
            raise ValueError("Circuit or Initial State MUST be defined.")
        result = self._circuit.execute(initial_state=self._initial_state)
        return result.state(numpy=True)
