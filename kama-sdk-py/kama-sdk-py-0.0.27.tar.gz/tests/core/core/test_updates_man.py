from copy import deepcopy
from typing import Dict, List

from kama_sdk.core.core import updates_man, consts
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import ReleaseDict
from kama_sdk.core.ktea.ktea_provider import ktea_client
from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager
from kama_sdk.utils import utils
from kama_sdk.utils.unittest.base_classes import ClusterTest
from kama_sdk.utils.unittest.helper import IdentityConfigMapVirtualKtea


class TestUpdatesMan(ClusterTest):

  def setUp(self):
    super(TestUpdatesMan, self).setUp()
    vktea_clients_manager.register_client(V2Ktea)
    v1_ktea = ktea_client()
    defaults = v1_ktea.load_default_values()
    config_man.patch_def_vars(defaults)

  def test_commit_new_ktea(self):
    """
    Ensure that after the update the ktea dict in the kamafile
    is updated to the correct values
    :return:
    """
    updates_man.commit_new_ktea(release)
    new_ktea = config_man.get_ktea_config()
    self.assertEqual('2', new_ktea['version'])
    self.assertEqual(V2Ktea.__name__, new_ktea['uri'])
    self.assertEqual(consts.KTEA_TYPE_VIRTUAL, new_ktea['type'])

  def test_commit_new_defaults_from_update(self):
    """
    Ensure that after the update the ktea dict in the Kamafile
    is updated to the correct values
    :return:
    """
    updates_man.commit_new_ktea(release)
    updates_man.commit_new_defaults_from_update(release)
    actual = config_man.get_default_vars()
    self.assertEqual(actual, v2_defaults)

  def test_preview_with_interfering(self):
    actual = updates_man.preview_manifest(release, consts.APP_SPACE_ID)
    print(actual)
    # TODO assert!


class V2Ktea(IdentityConfigMapVirtualKtea):
  def _template(self, values: Dict) -> List[Dict]:
    orig = deepcopy(super()._template(values)[0])
    return [utils.deep_merge(
      orig,
      dict(metadata=dict(annotations=dict(v=2)))
    )]

  def _default_values(self) -> Dict:
    return v2_defaults


release = ReleaseDict(
  id='x',
  version='2',
  ktea_type=consts.KTEA_TYPE_VIRTUAL,
  ktea_uri=V2Ktea.__name__,
  note='note',
  space=None
)


v2_defaults = {'k1': 2, 'k2': 2, 'k3': 2, 'k4': 2}
