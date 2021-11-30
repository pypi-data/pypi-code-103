from typing import List, Dict, Optional

from typing_extensions import TypedDict

from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY
from kama_sdk.utils import utils
from kama_sdk.core.core.types import KAO, ErrorCapture, K8sResDict
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.utils.logging import lwar


class ActionReturn(TypedDict):
  kaos: List[KAO]


ResDescs = List[K8sResDict]


class KubectlApplyAction(Action):

  def get_id(self) -> str:
    return super().get_id() or DEFAULT_ID

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> Optional[str]:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def res_descs(self) -> List[Dict]:
    return self.get_attr(RES_DESCS_KEY)

  def perform(self) -> ActionReturn:
    res_descs = self.res_descs()
    raise_on_res_descs_none(res_descs)
    if len(res_descs) > 0:
      kaos = KteaClient.kubectl_apply(res_descs)
      self.add_logs(list(map(utils.kao2log, kaos)))
      raise_on_kaos_with_error(kaos, res_descs)
      return ActionReturn(kaos=kaos)
    else:
      message = "skipped kubectl apply because 0 resources "
      lwar(message, sig=self.sig())
      self.add_logs([message])
      return ActionReturn(kaos=[])


def is_kao_error(kao: KAO) -> bool:
  return kao.get('error') is not None


def raise_on_res_descs_none(res_descs: List[Dict]):
  if res_descs is None:
    raise FatalActionError(ErrorCapture(
      type='kubectl_apply',
      reason='res_descs undefined, nothing to pass to kubectl',
      logs=['res_descs undefined']
    ))


def raise_on_kaos_with_error(outcomes: List[KAO], res_descs: ResDescs):
  if kao_culprit := next(filter(is_kao_error, outcomes), None):
    res_name = kao_culprit.get('name')
    res_kind = kao_culprit.get('kind')

    raise FatalActionError(ErrorCapture(
      type='kubectl_apply',
      reason=f'Resource rejected. kubectl apply failed'
             f' for {res_kind}/{res_name}',
      logs=[kao_culprit.get('error')],
      extras=dict(
        resource_signature=dict(name=res_name, kind=res_kind),
        resource=culprit_res_desc(kao_culprit, res_descs)
      )
    ))


def culprit_res_desc(culprit: KAO, descs: ResDescs) -> Optional[K8sResDict]:
  matcher = lambda desc: utils.are_res_same(culprit, utils.full_res2sig(desc))
  return next(filter(matcher, descs), None)


RES_DESCS_KEY = 'res_descs'
RET_KAOS_KEY = "kaos"

DEFAULT_ID = "sdk.action.kubectl_apply"
DEFAULT_TITLE = "Run kubectl apply"
DEFAULT_INFO = "Applies the templated manifest to the cluster"
