"""Matches predicates to their corresponding actions based on the common types."""
import copy
import logging
from typing import NoReturn, List, Tuple, Optional

from pddl.parser import Parser
from pddl.pddl import Type, Domain

from sam_learner.sam_models import SignatureType
from sam_learner.sam_models.comparable_predicate import ComparablePredicate
from sam_learner.sam_models.grounded_action import GroundedAction


def validate_no_duplicates(tested_list: List[str]) -> NoReturn:
	"""Validate that the predicate has only one possible match in the literal.

	:param tested_list: the list to test for duplicates.
	"""
	contains_duplicates = len(set(tested_list)) != len(tested_list)
	if contains_duplicates:
		raise ValueError(f"No duplications allowed! The predicates received - {tested_list}")


class PredicatesMatcher:
	"""Class that matches predicates according to the needed properties in the learning process."""

	matcher_domain: Domain
	logger: logging.Logger

	def __init__(self, domain_path: Optional[str] = None, domain: Optional[Domain] = None):
		self.logger = logging.getLogger(__name__)
		assert not (domain_path and domain)
		if domain_path is not None:
			self.matcher_domain = Parser(domain_path).parse_domain(read_from_file=True)

		if domain is not None:
			self.matcher_domain = Domain(
				name=domain.name,
				types=domain.types,
				predicates={name: ComparablePredicate(p.name, p.signature) for name, p in domain.predicates.items()},
				actions={},
				constants={name: constant for name, constant in domain.constants.items()}
			)

	def search_for_parameters_in_constants(
			self, possible_predicate: ComparablePredicate, grounded_predicate: ComparablePredicate) -> NoReturn:
		"""Search for a match in the constants.

		:param possible_predicate: the partially matched predicate created by the matcher.
		:param grounded_predicate: the grounded predicate that is seen in the trajectory.
		"""
		predicate_objects = [signature_item[0] for signature_item in grounded_predicate.signature]
		domain_predicate = self.matcher_domain.predicates[grounded_predicate.name]
		self.logger.debug("Searching for the predicate's parameters in the constants.")
		for index, constant_name in enumerate(self.matcher_domain.constants):
			if constant_name not in predicate_objects:
				continue

			literal_object_index = predicate_objects.index(constant_name)
			if domain_predicate.signature[literal_object_index] != \
					possible_predicate.signature[literal_object_index]:
				self.logger.debug("The parameters was already found in the action's signature, Skipping.")
				continue

			possible_predicate.signature[literal_object_index] = (
				constant_name, self.matcher_domain.constants[constant_name])

	def match_predicate_to_action_literals(
			self, grounded_predicate: ComparablePredicate,
			grounded_signature: SignatureType,
			lifted_signature: SignatureType) -> Optional[ComparablePredicate]:
		"""Match a literal to a possible lifted precondition for the input action.

		:param grounded_predicate: the grounded predicate that represent part of the previous state.
		:param grounded_signature: the signature of the action that contains the actual objects
			that the action was executed on.
		:param lifted_signature: the lifted signature of the action, is accessible from the
			trajectory.
		:return: a precondition, in case the action and the predicate contain matching objects,
			None otherwise.
		"""
		predicate_objects = [signature_item[0] for signature_item in grounded_predicate.signature]
		grounded_action_objects = [signature_item[0] for signature_item in grounded_signature]
		constants_names = []
		if len(self.matcher_domain.constants) > 0:
			constants_names = [name for name in self.matcher_domain.constants]

		validate_no_duplicates(predicate_objects)
		validate_no_duplicates(grounded_action_objects)

		if not set(predicate_objects).issubset(set(grounded_action_objects).union(constants_names)):
			self.logger.debug("The predicate does not match the action with the constants")
			return None

		domain_predicate = self.matcher_domain.predicates[grounded_predicate.name]
		possible_signature = [(item[0], item[1]) for item in domain_predicate.signature]
		possible_predicate_match: ComparablePredicate = ComparablePredicate(
			domain_predicate.name, possible_signature)
		for index, (action_object_name, object_types) in enumerate(grounded_signature):
			if action_object_name not in predicate_objects:
				continue

			literal_object_index = predicate_objects.index(action_object_name)
			parameter_name, parameter_types = lifted_signature[index]
			possible_predicate_match.signature[literal_object_index] = (
				parameter_name, parameter_types)

		self.search_for_parameters_in_constants(possible_predicate_match, grounded_predicate)
		return possible_predicate_match

	def get_possible_literal_matches(
			self, grounded_action: GroundedAction, literals: List[ComparablePredicate]) -> List[ComparablePredicate]:
		"""Get a list of possible preconditions for the action according to the previous state.

		:param grounded_action: the grounded action that was executed according to the trajectory.
		:param literals: the list of literals that we try to match according to the action.
		:return: a list of possible preconditions for the action that is being executed.
		"""
		possible_matches = []
		lifted_signature = grounded_action.lifted_signature
		grounded_signature = grounded_action.grounded_signature
		for predicate in literals:
			try:
				matches = self.match_predicate_to_action_literals(
					predicate, grounded_signature, lifted_signature)

			except ValueError as error:
				self.logger.debug(f"When parsing {grounded_action.activated_action_representation}, "
								  f"with the predicate {str(predicate)} "
								  f"got the error {error}! proceeding!")
				matches = None

			if matches is None:
				continue

			possible_matches.append(copy.deepcopy(matches))

		return possible_matches
