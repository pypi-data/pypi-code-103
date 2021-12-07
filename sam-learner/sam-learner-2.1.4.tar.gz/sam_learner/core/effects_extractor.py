"""Extract the effects from the state based on the exclusion and inclusion rules."""
from typing import Tuple, List, Set

from pddl.pddl import Predicate

from sam_learner.sam_models.comparable_predicate import ComparablePredicate
from sam_learner.sam_models.state import State


def extract_states_facts(
		previous_state: State, next_state: State) -> Tuple[Set[ComparablePredicate], Set[ComparablePredicate]]:
	"""extract the set of effects from the states.

	:param previous_state: the state that had been before the action was executed.
	:param next_state: the state after the action was executed.
	:return: the previous and the next states facts.
	"""
	prev_state_predicates = \
		set([ComparablePredicate(predicate=predicate) for predicate in previous_state.facts])
	next_state_predicates = \
		set([ComparablePredicate(predicate=predicate) for predicate in next_state.facts])
	return prev_state_predicates, next_state_predicates


def extract_effects(
		previous_state: State, next_state: State) -> Tuple[List[ComparablePredicate], List[ComparablePredicate]]:
	"""Extract the effects of the action according to the two lemmas that we know.

	:param previous_state: the state that had been before the action was executed.
	:param next_state: the state after the action was executed.
	:return: the add effects and the del effects.
	"""
	prev_state_predicates, next_state_predicates = extract_states_facts(previous_state, next_state)
	add_effects = next_state_predicates.difference(prev_state_predicates)
	del_effects = prev_state_predicates.difference(next_state_predicates)
	return list(add_effects), list(del_effects)


def extract_maybe_fluents(previous_state: State, next_state: State) -> List[ComparablePredicate]:
	"""Extract the `maybe` effects that will only be used for statistic reasons.

	:param previous_state: the state that had been before the action was executed.
	:param next_state: the state after the action was executed.
	:return: the list of predicates that could be used as the `maybe` effects.
	"""
	prev_state_predicates, next_state_predicates = extract_states_facts(previous_state, next_state)
	return list(prev_state_predicates.intersection(next_state_predicates))
