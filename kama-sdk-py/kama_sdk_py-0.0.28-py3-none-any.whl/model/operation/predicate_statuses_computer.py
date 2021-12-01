from typing import List, Optional

from kama_sdk.core.core.types import PredEval
from kama_sdk.utils.utils import any2bool
from kama_sdk.model.predicate.predicate import Predicate

class PredicateStatusesComputer:

  predicates: List[Predicate]
  _did_succeed: Optional[bool]
  explanations: List[str]
  evaluations: List[PredEval]

  def __init__(self, predicates: List[Predicate]):
    self.predicates = predicates
    self.evaluations = []
    self._did_succeed = None
    self.explanations = []

  def perform_iteration(self):
    self.explanations.clear()
    if len(self.predicates) > 0:
      self.evaluate_batch(self.get_optimist_predicates())
      if all_conditions_met(self.optimist_evaluations()):
        self.conclude(True)

      self.evaluate_batch(self.get_pessimist_predicates())
      if any_condition_met(self.pessimist_evaluations()):
        self.conclude(False)
    else:
      self.conclude(True)

  def evaluate_batch(self, predicates: List[Predicate]):
    for predicate in predicates:
      previous_eval = self.find_eval(predicate.get_id())
      if needs_recomputing(previous_eval, predicate.is_optimist()):
        new_eval = self.perform_pred_eval(predicate)
        self.process_new_evaluation(new_eval)
        if can_halt_early(new_eval, predicate):
          return

  def find_predicate(self, predicate_id: str) -> Predicate:
    finder = lambda predicate: predicate.get_id() == predicate_id
    return next(filter(finder, self.predicates), None)

  def find_eval(self, predicate_id: str) -> Optional[PredEval]:
    finder = lambda pred_eval: pred_eval['predicate_id'] == predicate_id
    return next(filter(finder, self.evaluations), None)

  def process_new_evaluation(self, new_eval: PredEval):
    prev_eval = self.find_eval(new_eval['predicate_id'])
    if prev_eval:
      prev_eval['met'] = new_eval['met']
      prev_eval['reason'] = new_eval['reason']
    else:
      self.evaluations.append(new_eval)

  def get_optimist_predicates(self) -> List[Predicate]:
    return [p for p in self.predicates if p.is_optimist()]

  def get_pessimist_predicates(self) -> List[Predicate]:
    return [p for p in self.predicates if not p.is_optimist()]

  def optimist_evaluations(self) -> List[PredEval]:
    decider = lambda e: self.find_predicate(e['predicate_id']).is_optimist()
    return list(filter(decider, self.evaluations))

  def pessimist_evaluations(self) -> List[PredEval]:
    decider = lambda e: not self.find_predicate(e['predicate_id']).is_optimist()
    return list(filter(decider, self.evaluations))

  def conclude(self, success: bool):
    self._did_succeed = success

  def did_finish(self) -> bool:
    return self._did_succeed is not None

  def did_fail(self):
    return self.did_finish() and not self._did_succeed

  def culprit_predicate(self) -> Predicate:
    filterer = filter(lambda e: e['met'], self.pessimist_evaluations())
    return self.find_predicate(next(filterer)['predicate_id'])

  def perform_pred_eval(self, predicate: Predicate) -> PredEval:
    raw_result = predicate.resolve()
    bool_result = any2bool(raw_result)

    if explanation := predicate.explanation():
      self.explanations.append(explanation)

    return PredEval(
      predicate_id=predicate.get_id(),
      met=bool_result,
      name=predicate.get_title(),
      reason=predicate.get_reason()
    )


def can_halt_early(pred_eval: PredEval, predicate: Predicate) -> bool:
  return pred_eval['met'] and not predicate.is_optimist()


def needs_recomputing(pred_eval: Optional[PredEval], is_optimist) -> bool:
  return not pred_eval or not is_optimist or not pred_eval['met']


def all_conditions_met(evaluations: List[PredEval]) -> bool:
  return set([s['met'] for s in evaluations]) == {True}


def any_condition_met(evaluations: List[PredEval]) -> bool:
  return True in [s['met'] for s in evaluations]
