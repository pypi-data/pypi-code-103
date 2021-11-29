from typing import List
from dataclasses import dataclass

@dataclass
class IterationState:
    """State of current iteration.

    Parameters
    ----------


    parameters: List[dict]
        List of parameters for each element in population
    best_parameters: dict
        Parameters with lowest loss value so far.
    loss: float = 9999999
        The loss from previous run
    lowest_loss: float = 9999999
        The lowest loss so far
    iterations: int = 0
        Number of iterations that have been ran.
    complete: bool = False
        True when iterator meets end conditions

    """
    parameters: List[dict]
    best_parameters: dict
    loss: float = 9999999
    lowest_loss: float = 9999999
    iterations: int = 0
    complete: bool = False

