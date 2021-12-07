"""Calculates the number of consistent models are extractable from the learned domain."""
import csv
import logging
from pathlib import Path
from typing import List, Set, NoReturn

from pddl.parser import Parser
from pddl.pddl import Domain, Action

from sam_learner.sam_models import ComparablePredicate

STATISTICS_COLUMNS_NAMES = ["domain_name", "domain_path", "action_name", "number_consistent_models"]


def calculate_number_consistent_models(
		maybe_preconditions: List[ComparablePredicate],
		maybe_effects: Set[ComparablePredicate] = frozenset()) -> int:
	"""calculates the number of consistent models that are available based on the learned preconditions and effects.

	:param maybe_preconditions: the possible preconditions for the learned action.
	:param maybe_effects: the possible effects for the learned action.
	:return: the total number of possible action models that could be learned for the specific action.
	"""
	return pow(2, len(maybe_preconditions)) * pow(2, len(maybe_effects))


class SafeConsistentModelsCalculator:

	def __init__(self):
		self.logger = logging.getLogger(__name__)

	def calculate_safe_models_consistency(
			self, generated_domains_directory_path: Path, output_statistics_path: str,
			known_actions: List[str]) -> NoReturn:
		"""

		:param generated_domains_directory_path:
		:param output_statistics_path:
		:param known_actions:
		:return:
		"""
		self.logger.info("Logging the number of consistent models for the safe action models that was learned.")
		consistency_statistics = []
		for generated_domain_path in generated_domains_directory_path.glob("*.pddl"):
			self.logger.debug(f"Logging the consistency statistics for the domain - {generated_domain_path.stem}")
			domain: Domain = Parser(generated_domain_path).parse_domain()
			learned_actions = [action_name for action_name in domain.actions if action_name not in known_actions]
			for action_name in learned_actions:
				action_data: Action = domain.actions[action_name]
				action_preconditions = action_data.precondition
				action_consistency = {
					"domain_name": domain.name,
					"domain_path": generated_domain_path,
					"action_name": action_name,
					"number_consistent_models": calculate_number_consistent_models(action_preconditions)
				}
				consistency_statistics.append(action_consistency)

		with open(output_statistics_path, "wt") as csv_file:
			writer = csv.DictWriter(csv_file, fieldnames=STATISTICS_COLUMNS_NAMES)
			writer.writeheader()
			for data in consistency_statistics:
				writer.writerow(data)
