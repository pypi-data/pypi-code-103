from typing import Any, List

from kama_sdk.utils import utils


def standard_comparison(operator: str, challenge: Any, against: Any) -> bool:
  challenge = utils.unmuck_primitives(challenge)
  against = utils.unmuck_primitives(against)

  try:
    if operator in ['equals', 'equal', 'eq', '==', '=']:
      return challenge == against

    elif operator in ['not-equals', 'not-equal', 'neq', '!=', '=/=']:
      return not challenge == against

    elif operator in ['is-in', 'in']:
      return challenge in against

    elif operator in ['contains']:
      return against in challenge

    elif operator in ['empty']:
      return not challenge or len(challenge) == 0

    elif operator in ['any', 'non-empty']:
      return isinstance(challenge, list) and len(challenge) > 0

    elif operator in ['many']:
      return isinstance(challenge, list) and len(challenge) > 1

    elif operator in ['only', 'contains-only']:
      if utils.is_listy(against):
        return set(challenge) <= set(against)
      else:
        return set(challenge) == {against}

    elif operator in ['is-greater-than', 'greater-than', 'gt', '>']:
      return challenge > against

    elif operator in ['gte', '>=']:
      return challenge >= against

    elif operator in ['is-less-than', 'less-than', 'lt', '<']:
      return challenge < against

    elif operator in ['lte', '<=']:
      return challenge <= against

    if operator in ['truthy', 'truthiness']:
      return utils.any2bool(challenge)

    if operator in ['falsy', 'falsiness', 'nullish']:
      return not utils.any2bool(challenge)

    elif operator in ['presence', 'defined', 'is-defined']:
      return bool(challenge)

    elif operator in ['undefined', 'is-undefined']:
      return not challenge

    print(f"Don't know operator {operator}")
    return False
  except:
    return False


def list_like_comparison(operator: str, challenge, against, on_many):
  run = lambda v: standard_comparison(operator, v, against)
  results: List[bool] = list(map(run, challenge))
  if on_many == 'each_true':
    return set(results) == {True}
  elif on_many == 'each_false':
    return set(results) == {False}
  elif on_many == 'some_true':
    return True in results
  elif on_many == 'some_false':
    return False in results
  else:
    print(f"[kama_sdk:predicate] bad many policy {on_many}")
