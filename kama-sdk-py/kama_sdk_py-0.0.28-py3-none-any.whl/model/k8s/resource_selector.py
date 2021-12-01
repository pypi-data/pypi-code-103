from typing import List, Dict, TypeVar, Type

from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.api_defs_man import api_defs_man

from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import K8sResDict
from kama_sdk.model.base.model import Model
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar
from kama_sdk.utils.utils import deep_get

T = TypeVar('T', bound='ResourceSelector')


class ResourceSelector(Model):

  @classmethod
  def inflate_with_literal(cls: Type[T], string: str, **kwargs) -> T:
    parts = string.split(':')
    return cls.inflate_with_config({
      RES_KIND_KEY: parts[len(parts) - 2],
      RES_NAME_KEY: parts[len(parts) - 1]
    }, **kwargs)

  def get_res_kind(self) -> str:
    return self.get_attr(RES_KIND_KEY, missing='raise')

  def get_res_name(self) -> str:
    return self.get_attr(RES_NAME_KEY)

  def get_res_ns(self) -> str:
    return self.get_attr(RES_NS_KEY, backup=config_man.get_ns())

  def get_label_selector(self) -> Dict:
    return self.get_attr(LABEL_SEL_KEY, depth=1) or {}

  def get_not_label_selector(self) -> Dict:
    return self.get_attr(NOT_LABEL_SEL_KEY, depth=1) or {}

  def get_field_selector(self) -> Dict:
    return self.get_attr(FIELD_SEL_KEY, depth=1) or {}

  def query_cluster(self) -> List[KatRes]:
    kat_class: KatRes = KatRes.class_for(self.get_res_kind())
    if kat_class:
      query_params = self.build_k8kat_query()
      if not kat_class.is_namespaced():
        del query_params['ns']
      try:
        return kat_class.list(**query_params)
      except:
        debug = {
          'res_kind': self.get_res_kind(),
          'namespace': self.get_res_ns(),
          **query_params
        }
        message = f"query error on {debug} (trace below)"
        lwar(message, sig=self.sig(), trace=True)
        return []
    else:
      print(f"[kama_sdk::resourceselector] DANGER no kat for {self.get_res_kind()}")
      return []

  def selects_kat_res(self, kat_res: KatRes) -> bool:
    return self.selects_res(utils.kres2dict(kat_res))

  def selects_res(self, res: K8sResDict) -> bool:
    res = fluff_resdict(res)

    kinds1 = api_defs_man.kind2plurname(self.get_res_kind())
    kinds2 = api_defs_man.kind2plurname(res['kind'])

    if kinds1 == kinds2 or self.get_res_kind() == '*':
      query_dict = self.build_k8kat_query()
      res_labels = (res.get('metadata') or {}).get('labels') or {}
      labels_match = query_dict['labels'].items() <= res_labels.items()
      fields_match = keyed_compare(query_dict['fields'], res)
      return labels_match and fields_match
      pass
    else:
      return False

  def get_api_group(self) -> str:
    if explicit := self.get_local_attr(API_GROUP_KEY):
      return explicit
    else:
      return api_defs_man.find_api_group(self.get_res_kind())

  def as_rest_bundle(self) -> Dict:
    return {
      'kind': self.get_res_kind(),
      'namespace': self.get_res_ns(),
      'group': self.get_api_group(),
      'version': 'v1',
      'label_selectors': self.get_label_selector(),
      'field_selectors': self.get_field_selector()
    }

  def build_k8kat_query(self) -> Dict:
    field_selector = self.get_field_selector()

    if self.get_res_name() and self.get_res_name() != '*':
      field_selector = {
        'metadata.name': self.get_res_name(),
        **(field_selector or {}),
      }

    return dict(
      ns=self.get_res_ns(),
      labels=self.get_label_selector(),
      not_labels=self.get_not_label_selector(),
      fields=field_selector
    )


def fluff_resdict(resdict: Dict) -> Dict:
  """
  This is foobar. Marked as debt.
  :param resdict:
  :return:
  """
  if 'metadata' not in resdict.keys():
    if 'name' in resdict.keys():
      return dict(
        **resdict,
        metadata=dict(name=resdict['name'])
      )
  return resdict


def keyed_compare(keyed_q_dict: Dict, against_dict: Dict) -> bool:
  for deep_key, check_val in keyed_q_dict.items():
    actual = deep_get(against_dict, deep_key)
    if not actual == check_val:
      return False
  return True


RES_KIND_KEY = 'res_kind'
RES_NAME_KEY = 'res_name'
API_GROUP_KEY = 'api_group'
RES_NS_KEY = 'namespace'
LABEL_SEL_KEY = 'label_selector'
NOT_LABEL_SEL_KEY = 'not_label_selector'
FIELD_SEL_KEY = 'field_selector'
