"""An extension to the predicate matcher that is able to cope with ambiguity in the executed actions."""
from itertools import permutations
from typing import List, Tuple, Optional

from pddl.pddl import Type, Domain

from sam_learner.sam_models import ComparablePredicate, SignatureType, GroundedAction
from .predicates_matcher import PredicatesMatcher


def create_signature_permutations(
        grounded_signature: SignatureType, lifted_signature: SignatureType,
        subset_size: int) -> List[Tuple[Tuple[str, Tuple[Type]], Tuple[str, Tuple[Type]]]]:
    """Choose r items our of a list size n.

    :param grounded_signature: the action's grounded signature.
    :param lifted_signature: the action's lifted signature.
    :param subset_size: the size of the subset.
    :return: a list containing subsets of the original list.
    """
    matching_signatures = zip(grounded_signature, lifted_signature)
    matching_permutations = list(permutations(matching_signatures, subset_size))

    return matching_permutations


class ExtendedMatcher(PredicatesMatcher):
    """An extended version of the predicate matcher class."""

    def __init__(self, domain_path: Optional[str] = None, domain: Optional[Domain] = None):
        super().__init__(domain_path, domain)

    def _is_matching_possible(self, grounded_signature: SignatureType, predicate_objects: List[str]) -> bool:
        """Test whether it is possible to match the predicate to the current action.

        :param grounded_signature: the action's grounded signature.
        :param predicate_objects: the names of the objects that appear in the predicate.
        :return: whether or not it is possible to match the predicate to the action based on the action's signature.
        """
        grounded_action_objects = [signature_item[0] for signature_item in grounded_signature]
        constants_names = [name for name in self.matcher_domain.constants]

        possible_grounded_matches = grounded_action_objects + constants_names
        if not all(predicate_obj in possible_grounded_matches for predicate_obj in predicate_objects):
            self.logger.debug("The predicate objects are not contained in the action's object, matching aborted.")
            return False

        return True

    def extended_predicate_matching(
            self, grounded_predicate: ComparablePredicate, grounded_signature: SignatureType,
            lifted_signature: SignatureType) -> Optional[List[ComparablePredicate]]:
        """The extended functionality that matches predicates to actions with duplicates.

        :param grounded_predicate: the grounded predicate that appeared in the trajectory.
        :param grounded_signature: the action's grounded signature.
        :param lifted_signature: the action's lifted signature.
        :return: the possible matching predicates.
        """
        predicate_objects = [signature_item[0] for signature_item in grounded_predicate.signature]
        if not self._is_matching_possible(grounded_signature, predicate_objects):
            return None

        constant_signature_items = [(name, (const_type,)) for name, const_type in self.matcher_domain.constants.items()]
        grounded_objects = grounded_signature + constant_signature_items
        lifted_objects = lifted_signature + constant_signature_items
        matching_signature_permutations = create_signature_permutations(
            grounded_objects, lifted_objects, len(predicate_objects))

        possible_matches = []
        for signature_option in matching_signature_permutations:
            lifted_match = []
            matching_grounded_action_objects = []
            for grounded_signature_item, lifted_signature_item in signature_option:
                lifted_match.append(lifted_signature_item)
                matching_grounded_action_objects.append(grounded_signature_item[0])

            if predicate_objects == matching_grounded_action_objects:
                possible_matches.append(ComparablePredicate(grounded_predicate.name, lifted_match))

        return possible_matches

    def match_predicate_to_action_literals(
            self, grounded_predicate: ComparablePredicate,
            grounded_signature: SignatureType,
            lifted_signature: SignatureType) -> Optional[List[ComparablePredicate]]:
        """Match a literal to a possible lifted precondition for the input action.

        Note:
            This method does not raise an error in case that there are duplications in either the state or the action.
            This method first tries to use the parent matching method. In case of an error being raised, the method
            will then rollback to the extended matching procedure.

        :param grounded_predicate: the grounded predicate that represent part of the previous state.
        :param grounded_signature: the signature of the action that contains the actual objects
            that the action was executed on.
        :param lifted_signature: the lifted signature of the action, is accessible from the
            trajectory.
        :return: a precondition, in case the action and the predicate contain matching objects,
            None otherwise.
        """
        try:
            match = super(ExtendedMatcher, self).match_predicate_to_action_literals(
                grounded_predicate, grounded_signature, lifted_signature)
            return None if match is None else [match]

        except ValueError:
            self.logger.debug("Found duplications in either the state of the action. Due to this fact, "
                              "rolling back to the extend matching procedure.")
            return self.extended_predicate_matching(grounded_predicate, grounded_signature, lifted_signature)

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
            matches = self.match_predicate_to_action_literals(predicate, grounded_signature, lifted_signature)
            if matches is None:
                continue

            possible_matches.extend(matches)

        return possible_matches
