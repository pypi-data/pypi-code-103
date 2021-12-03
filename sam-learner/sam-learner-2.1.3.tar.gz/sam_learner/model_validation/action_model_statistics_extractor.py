"""Module to extract statistics for the action model learner."""
import csv
import logging
import sys
from pathlib import Path
from typing import NoReturn, List, Dict, Any, Union

from pddl.parser import Parser
from pddl.pddl import Domain, Action

from sam_learner import SAMLearner, ESAMLearner
from sam_learner.core import DomainExporter
from sam_learner.core.trajectories_manager import TrajectorySerializationManager
from sam_learner.model_validation.action_precision_recall_calculator import PrecisionRecallCalculator
from sam_learner.model_validation.domain_comparison import validate_action_model
from sam_learner.sam_models.types import Trajectory

COLUMN_NAMES = [
    "domain_name",
    "num_trajectories",
    "num_domain_actions",
    "num_known_actions",
    "learned_actions_length",
    "domains_equal",
    "avg_trajectories_length",
    "learned_action_names",
    "error"]

LEARNED_ACTIONS_STATS_COLUMNS = [
    "domain_name",
    "num_trajectories",
    "num_trajectory_triplets",
    "learned_action_name",
    "num_triplets_action_appeared",
    "num_triplets_with_duplicate_parameters",
    "learned_preconditions",
    "learned_add_effects",
    "learned_delete_effects",
    "ground_truth_preconditions",
    "ground_truth_add_effects",
    "ground_truth_delete_effects",
    "preconditions_precision",
    "add_effects_precision",
    "delete_effects_precision",
    "preconditions_recall",
    "add_effects_recall",
    "delete_effects_recall",
]

SAM_LEARNING = "SAMLearning"
ESAM_LEARNING = "ESAMLearning"


def validate_no_redundant_actions(known_actions: List[str],
                                  learner: Union[SAMLearner, ESAMLearner]) -> NoReturn:
    """Validate that the initial state of the domain does not contain any redundant actions.

    :param known_actions: the names of the actions that the agent already knows.
    :param learner: the learning algorithm.
    """
    if known_actions is None:
        assert learner.learned_domain.actions == {}
    else:
        assert len(learner.learned_domain.actions) == len(known_actions)


class AMStatisticsExtractor:
    """Class that is used to extract statistics about the action model learner.

    Attributes:
        logger: the logger for the class.
        working_dir_path: the path to the directory containing the domain and the relevant files.
        expected_domain: the domain that contains all of the actions and the preconditions and
            effects.
        domain_exporter: the class that is able to export the domain to a PDDL file.
    """

    logger: logging.Logger
    workdir_path: str
    expected_domain: Domain
    domain_exporter: DomainExporter
    expected_domain_file_name: str
    trajectories_manager: TrajectorySerializationManager
    precision_recall_calculator: PrecisionRecallCalculator
    learning_algorithm: str

    def __init__(self, working_dir_path: str, expected_domain_path: str,
                 learning_algorithm: str = SAM_LEARNING):
        self.logger = logging.getLogger(__name__)
        self.workdir_path = working_dir_path
        self.expected_domain = Parser(expected_domain_path).parse_domain(read_from_file=True)
        self.expected_domain_file_name = f"{Path(expected_domain_path).stem}.pddl"
        self.domain_exporter = DomainExporter()
        self.trajectories_manager = TrajectorySerializationManager(
            workdir_path=Path(working_dir_path), domain_path=Path(expected_domain_path))
        self.precision_recall_calculator = PrecisionRecallCalculator(self.expected_domain)
        self.learning_algorithm = learning_algorithm

    def create_trajectories(self) -> List[Trajectory]:
        """Create the trajectories for the learner.

        :return: the trajectories needed to learn the action model.
        """
        self.logger.info("Creating the trajectories for the learner to use.")
        return self.trajectories_manager.create_trajectories()

    def _understand_learner_type(self, known_actions_map: Dict[str, Action]) -> Union[SAMLearner, ESAMLearner]:
        """

        :param known_actions_map:
        :return:
        """
        if self.learning_algorithm == SAM_LEARNING:
            return SAMLearner(working_directory_path=self.workdir_path, known_actions=known_actions_map,
                              domain_file_name=self.expected_domain_file_name)

        return ESAMLearner(working_directory_path=self.workdir_path, known_actions=known_actions_map,
                           domain_file_name=self.expected_domain_file_name)

    def run_learner(
            self, complete_statistics: List[Dict[str, any]], learned_actions_statistics: List[Dict[str, Any]],
            known_actions: List[str]) -> NoReturn:
        """Runs the learner and accumulates the statistics from the run.

        :param complete_statistics: the list of statistics that is to be accumulated.
        :param learned_actions_statistics: the statistics objects containing information about the learned actions.
        :param known_actions: the actions that the agent already know and thus there is no need to learn them.
        """
        available_trajectories = []
        domain_trajectories = self.create_trajectories()
        (Path(self.workdir_path) / "generated_domains").mkdir(exist_ok=True)
        for trajectory in domain_trajectories:
            statistics = {}
            available_trajectories.append(trajectory)
            known_actions_map = {name: self.expected_domain.actions[name] for name in known_actions}
            learner = self._understand_learner_type(known_actions_map)
            validate_no_redundant_actions(known_actions, learner)

            self.logger.debug(
                f"Trying to learn the action model with {len(available_trajectories)} trajectories.")
            try:
                learned_model = learner.learn_action_model(available_trajectories)
                actions_observation_histogram = learner.get_actions_appearance_histogram()
                actions_with_duplicated_params_histogram = learner.get_actions_with_duplicated_parameters_histogram()
                print("Finished learning the action model from the trajectories!")
                self.write_statistics_data(available_trajectories, learned_model, statistics, known_actions)
                self.precision_recall_calculator.write_learned_actions_statistics(
                    available_trajectories, learned_model, learned_actions_statistics, known_actions,
                    actions_observation_histogram, actions_with_duplicated_params_histogram)
                self.domain_exporter.export_domain(
                    learned_model,
                    Path(f"{self.workdir_path}/generated_domains/learned_domain-"
                         f"{len(available_trajectories)}-trajectories.pddl"))
            except ValueError as error:
                self.write_learning_error(error, statistics)
                available_trajectories.pop()

            complete_statistics.append(statistics)

    def write_learning_error(self, error: Exception, statistics: dict) -> NoReturn:
        """Write the appropriate statistics data in case that there is an error in the learning process.

        :param error: the error that was received while trying to learn the action model.
        :param statistics: the dictionary containing the statistics about the current run.
        """
        self.logger.warning(error)
        statistics["domain_name"] = self.expected_domain.name
        statistics["error"] = error

    def write_statistics_data(
            self, available_trajectories: List[Trajectory], learned_model: Domain, statistics: dict,
            known_actions: List[str]) -> NoReturn:
        """Write the statistics of the current execution of the code.

        :param available_trajectories: the available trajectories for the current execution.
        :param learned_model: the domain that was learned with the action model.
        :param statistics: the dictionary that contains the statistics collected during the
            entire program's execution.
        :param known_actions: the actions that were known to the model before the learning process started.
        :return:
        """
        num_trajectories = len(available_trajectories)
        statistics["domain_name"] = self.expected_domain.name
        statistics["num_trajectories"] = num_trajectories
        statistics["num_domain_actions"] = len(self.expected_domain.actions)
        statistics["num_known_actions"] = len(known_actions)
        statistics["learned_actions_length"] = len(learned_model.actions) - len(known_actions)
        statistics["domains_equal"] = validate_action_model(learned_model, self.expected_domain)
        statistics["avg_trajectories_length"] = sum([
            len(trajec) for trajec in available_trajectories]) / num_trajectories
        statistics["learned_action_names"] = "/".join([
            action for action in learned_model.actions if action not in known_actions])
        statistics["error"] = None

    def extract_action_model_statistics(self, stats_file_path: str, actions_stats_file_path: str,
                                        known_actions: List[str] = []) -> NoReturn:
        """Extract the statistics and saves them into a CSV file for future usage.

        :param stats_file_path: the path to the file that will contain the statistics.
        :param actions_stats_file_path: the path to the file containing data about the learned actions.
        :param known_actions: the names of the actions that the agent already knows.
        """
        domain_statistics = []
        learned_actions_statistics = []
        self.run_learner(domain_statistics, learned_actions_statistics, known_actions)
        with open(stats_file_path, 'wt', newline='') as domain_stats_csv_file, \
                open(actions_stats_file_path, 'wt', newline='') as actions_stats_csv_file:
            domain_data_writer = csv.DictWriter(domain_stats_csv_file, fieldnames=COLUMN_NAMES)
            actions_data_writer = csv.DictWriter(actions_stats_csv_file, fieldnames=LEARNED_ACTIONS_STATS_COLUMNS)
            domain_data_writer.writeheader()
            actions_data_writer.writeheader()
            for data in domain_statistics:
                domain_data_writer.writerow(data)

            for data in learned_actions_statistics:
                actions_data_writer.writerow(data)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        args = sys.argv
        workdir_path = args[1]
        complete_domain_path = args[2]
        statistics_output_path = args[3]
        actions_statistics_output_path = args[4]
        stats_extractor = AMStatisticsExtractor(workdir_path, complete_domain_path)
        stats_extractor.extract_action_model_statistics(statistics_output_path, actions_statistics_output_path)

    except Exception as e:
        print(e)
