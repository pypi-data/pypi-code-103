"""Module to calculate the precision and recall of our learning algorithm."""
import logging
from typing import List, Any, Dict, NoReturn

from pddl.pddl import Domain

from sam_learner.sam_models import Trajectory, ComparablePredicate


def calculate_true_positive_value(
		learned_predicates: List[ComparablePredicate], expected_predicates: List[ComparablePredicate]) -> int:
	"""

	:param learned_predicates:
	:param expected_predicates:
	:return:
	"""
	return len([predicate for predicate in learned_predicates if predicate in expected_predicates])


def calculate_false_positive_value(
		learned_predicates: List[ComparablePredicate], expected_predicates: List[ComparablePredicate]) -> int:
	"""

	:param learned_predicates:
	:param expected_predicates:
	:return:
	"""
	return len(learned_predicates) - calculate_true_positive_value(learned_predicates, expected_predicates)


def calculate_false_negative_value(
		learned_predicates: List[ComparablePredicate], expected_predicates: List[ComparablePredicate]) -> int:
	"""

	:param learned_predicates:
	:param expected_predicates:
	:return:
	"""
	return len(expected_predicates) - calculate_true_positive_value(learned_predicates, expected_predicates)


def calculate_recall(
		learned_predicates: List[ComparablePredicate], actual_predicates: List[ComparablePredicate]) -> float:
	"""

	:param learned_predicates:
	:param actual_predicates:
	:return:
	"""
	if len(learned_predicates) == 0:
		if len(actual_predicates) == 0:
			return 1

		return 0

	true_positives = calculate_true_positive_value(learned_predicates, actual_predicates)
	false_negatives = calculate_false_negative_value(learned_predicates, actual_predicates)
	return true_positives / (true_positives + false_negatives)


def calculate_precision(
		learned_predicates: List[ComparablePredicate], actual_predicates: List[ComparablePredicate]) -> float:
	"""

	:param learned_predicates:
	:param actual_predicates:
	:return:
	"""
	if len(learned_predicates) == 0:
		if len(actual_predicates) == 0:
			return 1

		return 0

	true_positives = calculate_true_positive_value(learned_predicates, actual_predicates)
	false_positives = calculate_false_positive_value(learned_predicates, actual_predicates)
	return true_positives / (true_positives + false_positives)


class PrecisionRecallCalculator:
	logger: logging.Logger
	expected_domain: Domain

	def __init__(self, expected_domain: Domain):
		self.logger = logging.getLogger(__name__)
		self.expected_domain = expected_domain

	def calculate_precision_recall_for_unknown_actions(
			self, action_name: str, num_trajectories: int, num_triplets: int) -> Dict[str, float]:
		"""

		:param action_name:
		:param num_trajectories:
		:param num_triplets:
		:return:
		"""
		actual_action_preconditions = self.expected_domain.actions[action_name].precondition
		actual_action_add_effects = list(self.expected_domain.actions[action_name].effect.addlist)
		actual_action_delete_effects = list(self.expected_domain.actions[action_name].effect.dellist)
		return {
			"domain_name": self.expected_domain.name,
			"num_trajectories": num_trajectories,
			"num_trajectory_triplets": num_triplets,
			"learned_action_name": action_name,
			"learned_preconditions": None,
			"learned_add_effects": None,
			"learned_delete_effects": None,
			"ground_truth_preconditions": ",".join([str(precondition) for precondition in actual_action_preconditions]),
			"ground_truth_add_effects": ",".join([str(add_effect) for add_effect in actual_action_add_effects]),
			"ground_truth_delete_effects": ",".join([str(del_effect) for del_effect in actual_action_delete_effects]),
			"preconditions_precision": 0,
			"add_effects_precision": 1,
			"delete_effects_precision": 1,
			"preconditions_recall": 1,
			"add_effects_recall": 0,
			"delete_effects_recall": 0,
		}

	def calculate_action_precision_recall(
			self, learned_model: Domain, action_name: str) -> Dict[str, float]:
		"""

		:param learned_model:
		:param action_name:
		:return:
		"""
		learned_action_preconditions = learned_model.actions[action_name].precondition
		learned_action_add_effects = list(learned_model.actions[action_name].effect.addlist)
		learned_action_delete_effects = list(learned_model.actions[action_name].effect.dellist)
		actual_action_preconditions = [ComparablePredicate(predicate=p) for p in self.expected_domain.actions[action_name].precondition]
		actual_action_add_effects = [ComparablePredicate(predicate=p) for p in self.expected_domain.actions[action_name].effect.addlist]
		actual_action_delete_effects = [ComparablePredicate(predicate=p) for p in self.expected_domain.actions[action_name].effect.dellist]
		return {
			"preconditions_precision": calculate_precision(learned_action_preconditions, actual_action_preconditions),
			"add_effects_precision": calculate_precision(learned_action_add_effects, actual_action_add_effects),
			"delete_effects_precision": calculate_precision(learned_action_delete_effects,
															actual_action_delete_effects),
			"preconditions_recall": calculate_recall(learned_action_preconditions, actual_action_preconditions),
			"add_effects_recall": calculate_recall(learned_action_add_effects, actual_action_add_effects),
			"delete_effects_recall": calculate_recall(learned_action_delete_effects, actual_action_delete_effects),
		}

	def extract_learned_action_data_vs_ground_truth(
			self, learned_model: Domain, action_name: str) -> Dict[str, str]:
		"""

		:param learned_model:
		:param action_name:
		:return:
		"""
		learned_action_preconditions = learned_model.actions[action_name].precondition
		learned_action_add_effects = list(learned_model.actions[action_name].effect.addlist)
		learned_action_delete_effects = list(learned_model.actions[action_name].effect.dellist)
		actual_action_preconditions = self.expected_domain.actions[action_name].precondition
		actual_action_add_effects = list(self.expected_domain.actions[action_name].effect.addlist)
		actual_action_delete_effects = list(self.expected_domain.actions[action_name].effect.dellist)
		return {
			"learned_preconditions": ",".join([str(precondition) for precondition in learned_action_preconditions]),
			"learned_add_effects": ",".join([str(add_effect) for add_effect in learned_action_add_effects]),
			"learned_delete_effects": ",".join([str(del_effect) for del_effect in learned_action_delete_effects]),
			"ground_truth_preconditions": ",".join([str(precondition) for precondition in actual_action_preconditions]),
			"ground_truth_add_effects": ",".join([str(add_effect) for add_effect in actual_action_add_effects]),
			"ground_truth_delete_effects": ",".join([str(del_effect) for del_effect in actual_action_delete_effects])
		}

	def write_learned_actions_statistics(
			self, available_trajectories: List[Trajectory], learned_model: Domain,
			learned_actions_statistics: List[Dict[str, Any]], known_actions: List[str],
			actions_observation_histogram: Dict[str, int],
			actions_with_duplicated_objects_observations: Dict[str, int],
	) -> NoReturn:
		"""Writes the statistics about the learned actions. This adds additional information about the learned actions.

		:param available_trajectories: the trajectories used in the learning process.
		:param learned_model: the action model that was learned.
		:param learned_actions_statistics: the dictionary containing the data about the learned actions.
		:param known_actions: the actions that the agent already knows.
		:param actions_with_duplicated_objects_observations: a mapping between the action and the number of times it was
			observed with duplicated objects.
		"""
		num_trajectories = len(available_trajectories)
		num_trajectory_triplets = sum([len(trajectory) for trajectory in available_trajectories])
		learned_actions = [
			action for action in learned_model.actions if action not in known_actions]
		for action_name in learned_actions:
			if action_name not in self.expected_domain.actions:
				self.logger.debug(f"Action - {action_name} is probably a proxy action. Real action not learned.")
				continue

			action_statistics = {
				"domain_name": self.expected_domain.name,
				"num_trajectories": num_trajectories,
				"num_trajectory_triplets": num_trajectory_triplets,
				"learned_action_name": action_name,
				"num_triplets_action_appeared": actions_observation_histogram[action_name],
				"num_triplets_with_duplicate_parameters": actions_with_duplicated_objects_observations[action_name]
			}
			action_statistics.update(
				self.extract_learned_action_data_vs_ground_truth(learned_model=learned_model, action_name=action_name))
			action_statistics.update(self.calculate_action_precision_recall(
				learned_model=learned_model, action_name=action_name))
			learned_actions_statistics.append(action_statistics)

		# writing the statistics for the actions that were not yet learned.
		not_yet_learned_action_names = [action_name for action_name in self.expected_domain.actions if
										action_name not in learned_model.actions]
		for not_learned_action in not_yet_learned_action_names:
			learned_actions_statistics.append(
				self.calculate_precision_recall_for_unknown_actions(
					not_learned_action, num_trajectories, num_trajectory_triplets))
