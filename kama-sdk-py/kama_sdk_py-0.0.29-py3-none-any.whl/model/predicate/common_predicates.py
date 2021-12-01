import random
import time

from kama_sdk.model.predicate.predicate import Predicate


class TruePredicate(Predicate):

  def get_id(self) -> str:
    return 'sdk.predicate.true'

  def perform_comparison(self, operator, challenge, check_against, on_many):
    return True


class FalsePredicate(Predicate):

  def get_id(self) -> str:
    return 'sdk.predicate.false'

  def perform_comparison(self, operator, challenge, check_against, on_many):
    return False


class RandomPredicate(Predicate):

  def get_id(self) -> str:
    return 'sdk.predicate.random'

  def perform_comparison(self, operator, challenge, check_against, on_many):
    time.sleep(1 if random.choice([True, False, False]) else 0)
    return random.choice([True, True, False])
