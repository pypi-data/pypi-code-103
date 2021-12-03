"""Module that contains the SAM learner code for single agent problems."""
import logging
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, NoReturn, Dict, Set

from pddl.pddl import Domain, Action, Effect
from pyperplan import Parser

from sam_learner.core import PredicatesMatcher, extract_effects, extract_maybe_fluents
from sam_learner.sam_models import GroundedAction, State, TrajectoryComponent, Trajectory, Mode, ComparablePredicate


def contains_duplicates(tested_list: List[str]) -> bool:
    """checks if the list contains duplicates.

    :param tested_list: the list to test for duplicates.
    :return: whether or not the list contains duplicates.
    """
    return len(set(tested_list)) != len(tested_list)


class SAMLearner:
    """Class that represents the safe action model learner algorithm."""

    logger: logging.Logger
    working_directory_path: Path
    trajectories: List[Trajectory]
    learned_domain: Domain
    matcher: PredicatesMatcher
    known_actions: Dict[str, Action]
    maybe_effects: Dict[str, Set[ComparablePredicate]]
    action_to_triplets_histogram: Dict[str, int]
    action_with_duplicate_param_calls: Dict[str, int]

    def __init__(
            self, working_directory_path: Optional[str] = None, domain_file_name: str = "domain.pddl",
            mode: Mode = "production",
            domain: Optional[Domain] = None, known_actions: Dict[str, Action] = {}):
        self.logger = logging.getLogger(__name__)
        self.known_actions = known_actions
        self.maybe_effects = defaultdict(set)
        self.action_to_triplets_histogram = defaultdict(int)
        self.action_with_duplicate_param_calls = defaultdict(int)
        if mode == "development":
            self.matcher = PredicatesMatcher(domain=domain)
            self.learned_domain = domain
            return

        self.working_directory_path = Path(working_directory_path)
        domain_path = self.working_directory_path / domain_file_name
        self.learned_domain = Parser(domain_path).parse_domain(read_from_file=True)
        self.learned_domain.actions = {}
        self.matcher = PredicatesMatcher(domain_path=str(domain_path))
        if known_actions is not None:
            self.learned_domain.actions = {
                name: action for name, action in known_actions.items()
            }

    def handle_action_effects(
            self, grounded_action: GroundedAction, previous_state: State, next_state: State) -> Effect:
        """Finds the effects generated from the previous and the next state on this current step.

        :param grounded_action: the grounded action that was executed according to the trajectory.
        :param previous_state: the state that the action was executed on.
        :param next_state: the state that was created after executing the action on the previous
            state.
        :return: the effect containing the add and del list of predicates.
        """
        grounded_add_effects, grounded_del_effects = extract_effects(previous_state, next_state)
        action_effect = Effect()
        action_effect.addlist = action_effect.addlist.union(self.matcher.get_possible_literal_matches(
            grounded_action, grounded_add_effects))
        action_effect.dellist = action_effect.dellist.union(self.matcher.get_possible_literal_matches(
            grounded_action, grounded_del_effects))

        self.handle_maybe_effects(grounded_action, previous_state, next_state)

        return action_effect

    def handle_maybe_effects(
            self, grounded_action: GroundedAction, previous_state: State, next_state: State) -> NoReturn:
        """Extracts the maybe effects that are caused by the intersection between the previous and the next state.

        :param grounded_action: the currently used grounded action.
        :param previous_state: the state that the action was executed on.
        :param next_state: the state that was created after executing the action on the previous
            state.
        """
        maybe_effect_fluents = extract_maybe_fluents(previous_state, next_state)
        maybe_effects = self.matcher.get_possible_literal_matches(grounded_action, maybe_effect_fluents)
        action_name = grounded_action.lifted_action_name
        if action_name in self.maybe_effects:
            self.maybe_effects[action_name].intersection_update(maybe_effects)
        else:
            self.maybe_effects[action_name].update(maybe_effects)

    def add_new_action(
            self, grounded_action: GroundedAction, previous_state: State, next_state: State) -> NoReturn:
        """Create a new action in the domain.

        :param grounded_action: the grounded action that was executed according to the trajectory.
        :param previous_state: the state that the action was executed on.
        :param next_state: the state that was created after executing the action on the previous
            state.
        """
        self.logger.info(f"Adding the action {grounded_action.activated_action_representation} "
                         f"to the domain.")
        new_action = Action(name=grounded_action.lifted_action_name,
                            signature=grounded_action.lifted_signature,
                            precondition=[],
                            effect=None)

        # adding the preconditions each predicate is grounded in this stage.
        possible_preconditions = self.matcher.get_possible_literal_matches(grounded_action,
                                                                           previous_state.facts)
        new_action.precondition = list(set(possible_preconditions))

        action_effect = self.handle_action_effects(grounded_action, previous_state, next_state)
        new_action.effect = action_effect
        self.learned_domain.actions[new_action.name] = new_action
        self.logger.debug(
            f"Finished adding the action {grounded_action.activated_action_representation}.")

    def _is_known_action(self, action_name: str) -> bool:
        """Check whether or not the input action is an action that the agent shouldn't learn.

        :param action_name: the name of the action that is currently observed in the trajectory.
        :return: whether or not the action is already known to the agent.
        """
        self.logger.info(f"Updating the action - {action_name}")
        if action_name in self.known_actions:
            self.logger.debug(f"The action {action_name} is already known to the agent. Skipping!")
            return True

        return False

    def update_action(
            self, grounded_action: GroundedAction, previous_state: State, next_state: State) -> NoReturn:
        """Create a new action in the domain.

        :param grounded_action: the grounded action that was executed according to the trajectory.
        :param previous_state: the state that the action was executed on.
        :param next_state: the state that was created after executing the action on the previous
            state.
        """
        action_name = grounded_action.lifted_action_name
        if self._is_known_action(action_name):
            return

        current_action: Action = self.learned_domain.actions[action_name]
        self._update_action_preconditions(current_action, grounded_action, previous_state)

        action_effect: Effect = self.handle_action_effects(
            grounded_action, previous_state, next_state)
        current_action.effect.addlist = current_action.effect.addlist.union(action_effect.addlist)
        current_action.effect.dellist = current_action.effect.dellist.union(action_effect.dellist)
        self.logger.debug(f"Done updating the action - {grounded_action.lifted_action_name}")

    def _update_action_preconditions(
            self, current_action: Action, grounded_action: GroundedAction, previous_state: State) -> NoReturn:
        """Updates the preconditions of an action after it was observed at least once.

        :param current_action: the action that is being observed.
        :param grounded_action: the grounded action that is being executed in the trajectory component.
        :param previous_state: the state that was seen prior to the action's execution.
        """
        model_preconditions = current_action.precondition.copy()
        possible_preconditions = self.matcher.get_possible_literal_matches(
            grounded_action, previous_state.facts)
        if len(possible_preconditions) > 0:
            for precondition in model_preconditions:
                if precondition not in possible_preconditions:
                    current_action.precondition.remove(precondition)
        else:
            self.logger.warning(f"while handling the action {grounded_action.activated_action_representation} "
                                f"inconsistency occurred, since we do not allow for duplicates we do not update the "
                                f"preconditions.")

    def _verify_parameter_duplication(self, grounded_action: GroundedAction) -> NoReturn:
        """Verifies if the action was called with duplicated objects in a trajectory component.

        :param grounded_action: the grounded action observed in the trajectory triplet.
        """
        predicate_objects = [signature_item[0] for signature_item in grounded_action.grounded_signature]
        if contains_duplicates(predicate_objects):
            self.action_with_duplicate_param_calls[grounded_action.lifted_action_name] += 1

    def handle_single_trajectory_component(self, component: TrajectoryComponent) -> NoReturn:
        """Handles a single trajectory component as a part of the learning process.

        :param component: the trajectory component that is being handled at the moment.
        """
        previous_state = component.previous_state
        grounded_action = component.grounded_action
        next_state = component.next_state
        action_name = grounded_action.lifted_action_name
        if self._is_known_action(action_name):
            self.logger.debug(f"The action - {action_name} is already known to the agent.")
            return

        self._verify_parameter_duplication(grounded_action)
        self.action_to_triplets_histogram[action_name] += 1
        if action_name not in self.learned_domain.actions:
            self.add_new_action(grounded_action, previous_state, next_state)

        else:
            self.update_action(grounded_action, previous_state, next_state)

    def get_actions_appearance_histogram(self) -> Dict[str, int]:
        """Returns the histogram value of the learned actions.

        :return: the histogram of the learned actions.
        """
        return self.action_to_triplets_histogram

    def get_actions_with_duplicated_parameters_histogram(self) -> Dict[str, int]:
        """Returns the histogram value of the learned actions with the duplicated objects.

        :return: the histogram of the learned actions where their usage contained duplicated objects.
        """
        return self.action_with_duplicate_param_calls

    def learn_action_model(self, trajectories: List[Trajectory]) -> Domain:
        """Learn the SAFE action model from the input trajectories.

        :param trajectories: the list of trajectories that are used to learn the safe action model.
        :return: a domain containing the actions that were learned.
        """
        self.logger.info("Starting to learn the action model!")
        for trajectory in trajectories:
            for component in trajectory:
                self.handle_single_trajectory_component(component)

        return self.learned_domain
