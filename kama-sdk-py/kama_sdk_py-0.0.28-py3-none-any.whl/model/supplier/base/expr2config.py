from typing import Dict, List, Tuple, Optional

from kama_sdk.utils.logging import lwar
from kama_sdk.model.base import mc


"""
Functions that perform the translation from syntactically sugared
Model/Supplier invokations into descriptors. The expressions handled
here are >>, ->, and =>.
"""


def expr2config(orig: str) -> Dict:
  if early_win := special_case_desc_or_none(orig):
    return early_win
  else:
    tokens = tokenize(orig)
    result = tokens2tree(tokens)
    return result


def tokenize(expr: str) -> List[str]:
  result = []
  part = expr
  end_reached = False
  while not end_reached:
    hit = first_sym_ind(part)
    if hit:
      start, end, sym = hit
      result.append(part[0:start])
      result.append(part[start:end+1])
      part = part[(end + 1):]
    else:
      result.append(part)
      end_reached = True
  return result


def first_sym_ind(part: str) -> Optional[Tuple[int, int, str]]:
  symbols = list(ser_mapping().keys())
  winner = None
  for sym in symbols:
    if sym in part:
      index = part.index(sym)
      if not winner or winner[0] > index:
        winner = (index, index + len(sym) - 1, sym)
  return winner


def tokens2tree(parts: List[str]) -> Dict:
  """

  :param parts:
  :return:
  """
  if len(parts) == 1:
    return polymorphic_expr_to_config(parts[0])
  elif len(parts) == 3:
    return case_of_three(tuple(parts))
  elif len(parts) > 3:
    return case_of_more_than_three(parts)
  else:
    lwar(f"malformed expr {parts}")
    return {}


def case_of_three(tup: Tuple) -> Dict:
  from kama_sdk.model.supplier.base import supplier
  identity, symbol, output = tup
  return {
    **polymorphic_expr_to_config(identity),
    supplier.SERIALIZER_KEY: ser_mapping()[symbol],
    supplier.OUTPUT_FMT_KEY: output
  }


def case_of_more_than_three(parts):
  from kama_sdk.model.supplier.base import supplier
  from kama_sdk.model.supplier.base.supplier import Supplier

  output_expr = parts[len(parts) - 1]
  serializer_symbol = parts[len(parts) - 2]
  serializer_type = ser_mapping()[serializer_symbol]
  rem_on_left = parts[0:(len(parts) - 2)]
  return {
    mc.KIND_KEY: Supplier.__name__,
    supplier.SERIALIZER_KEY: serializer_type,
    supplier.OUTPUT_FMT_KEY: output_expr,
    supplier.SRC_DATA_KEY: tokens2tree(rem_on_left)
  }


def polymorphic_expr_to_config(expr: str) -> Dict:
  from kama_sdk.model.supplier.base.special_suppliers import SelfSupplier
  if expr == mc.SELF_LOOKUP_SUGAR:
    return {mc.KIND_KEY: SelfSupplier.__name__}
  if expr == mc.PARENT_LOOKUP_SUGAR:
    from kama_sdk.model.supplier.base.special_suppliers import ParentSupplier
    return {mc.KIND_KEY: ParentSupplier.__name__}
  elif expr.startswith(mc.LAZY_SYMBOL):
    un_ref_expr = expr[len(mc.LAZY_SYMBOL):]
    return delayed_expr_to_config(un_ref_expr)
  else:
    return direct_expr_to_config(expr)


def delayed_expr_to_config(expr: str) -> Dict:
  if expr.startswith(mc.ID_REFERENCE_PREFIX):
    actual = expr[len(mc.ID_REFERENCE_PREFIX):]
    return delayed_inherit_expr_to_config(actual)
  elif expr.startswith(mc.KIND_REFERENCE_PREFIX):
    actual = expr[len(mc.KIND_REFERENCE_PREFIX):]
    return delayed_kind_expr_to_config(actual)
  else:
    return delayed_inherit_expr_to_config(expr)


def delayed_kind_expr_to_config(kind_expr: str) -> Dict:
  from kama_sdk.model.supplier.base import supplier
  from kama_sdk.model.supplier.base.special_suppliers import DelayedInflateSupplier
  return {
    mc.KIND_KEY: DelayedInflateSupplier.__name__,
    supplier.SRC_DATA_KEY: {
      mc.KIND_KEY: kind_expr
    },
  }


def delayed_inherit_expr_to_config(model_id) -> Dict:
  from kama_sdk.model.supplier.base import supplier
  from kama_sdk.model.supplier.base.special_suppliers import DelayedInflateSupplier
  return {
    mc.KIND_KEY: DelayedInflateSupplier.__name__,
    supplier.SRC_DATA_KEY: model_id,
  }


def direct_expr_to_config(expr: str) -> Dict:
  if expr.startswith(mc.ID_REFERENCE_PREFIX):
    actual = expr[len(mc.ID_REFERENCE_PREFIX):]
    return direct_inherit_expr_to_config(actual)
  elif expr.startswith(mc.KIND_REFERENCE_PREFIX):
    actual = expr[len(mc.KIND_REFERENCE_PREFIX):]
    return direct_kind_expr_2_config(actual)
  else:
    return direct_inherit_expr_to_config(expr)


def direct_inherit_expr_to_config(id_expr: str):
  from kama_sdk.model.supplier.base.supplier import Supplier
  return {
    mc.KIND_KEY: Supplier.__name__,
    mc.INHERIT_KEY: id_expr
  }


def direct_kind_expr_2_config(kind_name: str):
  return {
    mc.KIND_KEY: kind_name
  }


def special_case_desc_or_none(expr: str):
  if expr == mc.NS_LOOKUP_KEY:
    from kama_sdk.model.supplier.ext.biz.config_supplier import NamespaceSupplier
    return {mc.KIND_KEY: NamespaceSupplier.__name__}
  else:
    return None


def ser_mapping() -> Dict[str, str]:
  from kama_sdk.model.supplier.base import supplier
  return {
    ">>": supplier.SER_MODEL_ATTR,
    "->": supplier.SER_JQ,
    "=>": supplier.SER_NATIVE
  }
