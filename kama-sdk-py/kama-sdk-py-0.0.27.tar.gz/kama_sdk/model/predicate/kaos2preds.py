from typing import List, Optional

from kama_sdk.core.core import consts
from kama_sdk.core.core.types import KAO
from kama_sdk.model.base.common import RESOURCE_SELECTOR_KEY
from kama_sdk.model.base.mc import KIND_KEY, ID_KEY, TITLE_KEY
from kama_sdk.model.k8s import resource_selector as res_sel
from kama_sdk.model.predicate import predicate as pred
from kama_sdk.model.predicate.predicate import Predicate, CHALLENGE_KEY, EXPLAIN_KEY, ON_MANY_KEY, OPERATOR_KEY, \
  IS_OPTIMISTIC_KEY, CHECK_AGAINST_KEY, REASON_KEY
from kama_sdk.model.supplier.base import supplier as sup
from kama_sdk.model.supplier.base.supplier import OUTPUT_FMT_KEY, SERIALIZER_KEY, IS_MANY_KEY
from kama_sdk.utils import utils

"""
Module that does the work of generating Predicates from 
kubectl-apply logs. 
"""


def _kao_discriminator(kao: Optional[KAO]) -> bool:
  return kao and not kao.get('verb') == 'unchanged'


def kaos2predicates(kaos: List[KAO]) -> List[Predicate]:
  """
  Given a list of kubectl-apply-outcomes (KAO), maps each one
  to two predicates that determine whether the resource from the KAO
  has settled to a positive or negative state. The state of a resource comes
  from KatRes's 'ternary_status', which is either positive, negative,
  or pending.
  :param kaos: list of KAO
  :return:
  """
  predicates = dict(positive=[], negative=[])
  for ktl_outcome in list(filter(_kao_discriminator, kaos)):
    if not ktl_outcome['verb'] == 'unchanged':
      for charge in [consts.POS_STATUS, consts.NEG_STATUS]:
        predicate = kao2predicate(ktl_outcome, charge)
        predicates[charge].append(predicate)
  return utils.flatten(list(predicates.values()))


def kao2predicate(kao: KAO, charge: str) -> Predicate:
  """
  Assembles a Predicate that checks for a resource settled state,
  either positive or negative, based on kubectl-apply-outcome.
  The predicate's `challenge` is a ResourcesSupplier that will
  resolves to the resource's `ternary_status`. The `ternary_status`
  is then checked against the `charge`. The charge is also patched onto
  the predicate for consumption by an AwaitSettledAction.
  :param kao: kubectl-apply-outcome
  :param charge: positive or negative
  :return: inflated Predicate
  """
  from kama_sdk.model.supplier.ext.biz.resources_supplier import ResourcesSupplier

  kind, name = utils.values_at(kao, 'kind', 'name')

  selector = {
    res_sel.RES_KIND_KEY: kind,
    res_sel.RES_NAME_KEY: name,
    'api_group': kao['api_group']
  }

  word = "settled" if charge == consts.POS_STATUS else 'broken'
  check_part = f"Check {word}: {kind}/{name}.status"
  challenge_part = f"${{get::self>>resolved_{pred.CHALLENGE_KEY}}}"
  whole = f"{check_part} = {challenge_part}"

  return Predicate({
    KIND_KEY: Predicate.__name__,
    ID_KEY: f"{kind}/{name}-{charge}",
    TITLE_KEY: f"{kind}/{name} is {charge}",
    REASON_KEY: f"Checking that {kind}/{name} is {charge} failed",
    CHECK_AGAINST_KEY: charge,
    IS_OPTIMISTIC_KEY: charge == consts.POS_STATUS,
    OPERATOR_KEY: '=',
    ON_MANY_KEY: 'each_true',
    EXPLAIN_KEY: whole,
    CHALLENGE_KEY: {
      KIND_KEY: ResourcesSupplier.__name__,
      ID_KEY: f"{kind}/{name}-{charge}-selector",
      OUTPUT_FMT_KEY: 'ternary_status',
      SERIALIZER_KEY: sup.SER_NATIVE,
      IS_MANY_KEY: True,
      RESOURCE_SELECTOR_KEY: selector
    },
    pred.ERROR_EXTRAS_KEY: dict(
      resource_signature={
        'kind': kind,
        'name': name
      },
    )})
