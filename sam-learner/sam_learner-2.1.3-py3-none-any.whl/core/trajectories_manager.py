"""Module to handle the storing loading and updating of a trajectory."""
import logging
import os
import pickle
from pathlib import Path
from typing import Tuple, List, NoReturn, Optional

from pddl.pddl import Domain
from sam_learner.core import TrajectoryGenerator
from sam_learner.sam_models import Trajectory


class TrajectorySerializationManager:
    """class that manages the serialization processes of the trajectories."""

    working_directory_path: Path
    logger: logging.Logger
    domain_path: Path

    def __init__(self, workdir_path: Path, domain_path: Path):
        self.working_directory_path = workdir_path
        self.domain_path = domain_path
        self.logger = logging.getLogger(__name__)

    def get_problem_and_solution_files(self) -> List[Tuple[Path, Path]]:
        """Get the problem and the solution file paths from the working directory.

        :return: the paths to the problems and their respected plans.
        """
        paths = []
        for solution_file_path in self.working_directory_path.glob("*.solution"):
            problem_file_name = solution_file_path.stem.split("_plan")[0]
            problem_path = self.working_directory_path / f"{problem_file_name}.pddl"
            paths.append((problem_path, solution_file_path))

        return paths

    def create_trajectories(self, serialization_file_name: Optional[str] = None) -> List[Trajectory]:
        """Create the trajectories that will be used in the main algorithm.

        :return: the list of trajectories that will be used in the SAM algorithm.
        """
        self.logger.info("Creating the trajectories for the algorithm.")
        trajectories = []
        if serialization_file_name is not None:
            stored_trajectories_path = self.working_directory_path / serialization_file_name

        else:
            stored_trajectories_path = self.working_directory_path / "saved_trajectories"

        if stored_trajectories_path.exists():
            return self.load_trajectories(stored_trajectories_path)

        for problem_path, plan_path in self.get_problem_and_solution_files():
            generator = TrajectoryGenerator(str(self.domain_path), str(problem_path))
            trajectories.append(generator.generate_trajectory(str(plan_path)))

        self.store_trajectories(stored_trajectories_path, trajectories)
        return trajectories

    def create_trajectories_fama_format(self) -> Tuple[List[Path], List[Trajectory]]:
        """Create the trajectories in the files that FAMA learner can use in the learning process.

        :return: the list of paths to the trajectories.
        """
        self.logger.info("Creating the trajectories for the FAMA algorithm in the correct format.")
        trajectory_paths = []
        generated_trajectories = []
        for index, (problem_path, plan_path) in enumerate(self.get_problem_and_solution_files()):
            generator = TrajectoryGenerator(str(self.domain_path), str(problem_path))
            fama_trajectory, generated_trajectory = generator.create_trajectory_in_fama_format(plan_path)
            trajectory_file_path = self.working_directory_path / f"{self.domain_path.stem}_trajectory{index}"
            trajectory_paths.append(trajectory_file_path)
            generated_trajectories.append(generated_trajectory)
            with open(trajectory_file_path, 'w') as output:
                output.write(fama_trajectory)

        return trajectory_paths, generated_trajectories

    def load_trajectories(self, stored_trajectories_path: Path) -> List[Trajectory]:
        """Loads the trajectories from the trajectories file.

        :param stored_trajectories_path: the path to the files that stores the trajectories.
        :return: the loaded deserialized trajectories.
        """
        self.logger.debug("Loading the trajectories from the file!")
        with open(stored_trajectories_path, "rb") as trajectories_file:
            return pickle.load(trajectories_file)

    def store_trajectories(self, stored_trajectories_path: Path, trajectories: List[Trajectory]) -> NoReturn:
        """Store the trajectories in the trajectory file so that future runs of the algorithm would be faster.

        :param stored_trajectories_path: the path to the file that stores the trajectories.
        :param trajectories: the trajectories that are to be stored in the file.
        """
        with open(stored_trajectories_path, "wb") as trajectories_file:
            self.logger.debug("Saving the created trajectories in a file for future usage.")
            pickle.dump(trajectories, trajectories_file)

    def update_stored_trajectories(self, trajectory: Trajectory, save_path: Optional[Path] = None) -> NoReturn:
        """Serialize the new trajectory.

        :param trajectory: the trajectory to serialize.
        :param save_path: the path to the file that saves the trajectories.
        """
        trajectories_path = self.working_directory_path / "saved_trajectories" if save_path is None else save_path
        with open(trajectories_path, "rb") as trajectories_file:
            trajectories = pickle.load(trajectories_file)

        trajectories.append(trajectory)
        self.store_trajectories(trajectories_path, trajectories)

    def delete_trajectories_file(self, trajectories_file_path: Optional[Path] = None) -> NoReturn:
        """deletes the file that contains the saved trajectories.

        :param trajectories_file_path: the path to the trajectories file.
        """
        trajectories_path = self.working_directory_path / "saved_trajectories" if \
            trajectories_file_path is None else trajectories_file_path
        os.remove(trajectories_path)
