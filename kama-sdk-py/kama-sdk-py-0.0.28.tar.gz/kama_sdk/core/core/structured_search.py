import re
from typing import Dict, Union, List, Any

from kama_sdk.utils import utils
from kama_sdk.core.core.comparison import standard_comparison
from kama_sdk.utils.logging import lwar


Selection = Union[str, List, bool, None]
SelDict = Dict[str, Union[Dict, Selection]]
Dicts = List[Dict]


def query(selector_expr: SelDict, candidates: Dicts) -> Dicts:
  if selector_expr:
    return [d for d in candidates if is_query_match(selector_expr, d)]
  else:
    return candidates


def is_query_match(selector: SelDict, challenge: Dict) -> bool:
  if challenge:
    flat_selector = utils.deep2flat(selector)
    for flat_selector_key, select_expr in flat_selector.items():
      local_challenge = utils.deep_get(challenge, flat_selector_key)
      result = is_terminal_match(select_expr, local_challenge)
      if not result:
        return False
    return True
  else:
    return False


def is_terminal_match(select_expr: Any, actual: Any) -> bool:
  if isinstance(select_expr, str) and select_expr.startswith("expr::"):
    post = select_expr.split("expr::")[1]
    operator, check_against = None, None
    if "::" in post:
      operator, check_against = post.split("::")
    else:
      operator = post
    return standard_comparison(operator, actual, check_against)
  else:
    return is_terminal_match2(select_expr, actual)


def is_terminal_match2(select_expr: Selection, candidate: Any) -> bool:
  if isinstance(select_expr, list):
    # if isinstance(candidate, list):
    #   for one_candidate in candidate:
    #     sub_results = [is_terminal_match2(s, candidate) for s in select_expr]
    #
    # else:
    sub_results = [is_terminal_match2(s, candidate) for s in select_expr]
    return True in sub_results
  elif isinstance(select_expr, str):
    try:
      re_match = re.compile(select_expr).fullmatch(candidate)
      return re_match is not None
    except:
      return False
  elif select_expr in [True, False]:
    return candidate == select_expr
  elif select_expr is None:
    return candidate is None
  else:
    lwar(f"universal_match bad type {type(select_expr)}")
    return False
