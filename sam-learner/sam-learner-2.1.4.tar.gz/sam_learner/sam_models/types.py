"""Contains the new types for the action model learner."""
from typing import List, Literal, Tuple

from pddl.pddl import Type

from sam_learner.sam_models.trajectory_component import TrajectoryComponent

Trajectory = List[TrajectoryComponent]
SignatureType = List[Tuple[str, Tuple[Type]]]
Mode = Literal["production", "development"]
