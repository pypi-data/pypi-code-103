import unittest

import dotenv
from k8kat.auth.kube_broker import broker
from k8kat.utils.testing import ns_factory

from kama_sdk.core.ktea.vktea_clients_manager import vktea_clients_manager
from kama_sdk.model.base.model import Model
from kama_sdk.utils import env_utils
from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.utils.unittest import helper


class KamaTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super().setUpClass()
    if not is_env_ready():
      dotenv.load_dotenv()
      env_utils.set_run_env('test')
      update_readiness(True, False)

  def setUp(self) -> None:
    super().setUp()
    config_man._ns = None
    models_manager.clear(restore_defaults=True)

  def tearDown(self) -> None:
    super().setUp()
    config_man._ns = None
    models_manager.clear(restore_defaults=True)  # TODO defaults=false, no?


class ClusterTest(KamaTest):

  @classmethod
  def setUpClass(cls) -> None:
    super().setUpClass()
    if not is_k8s_ready():
      broker.connect()
      update_readiness(True, True)

  def setUp(self) -> None:
    super().setUp()
    config_man.invalidate_cmap()
    vktea_clients_manager.clear()
    ns_factory.update_max_ns(20)
    config_man._ns, = ns_factory.request(1)
    helper.create_base_kamafile(config_man.get_ns())
    helper.set_and_register_trivial_vtam()

  def tearDown(self) -> None:
    super(ClusterTest, self).tearDown()
    helper.clear_trivial_vtam()

  @classmethod
  def tearDownClass(cls) -> None:
    super().tearDownClass()
    ns_factory.relinquish_all()


test_ready_obj = {
  'env_ready': False,
  'k8s_ready': False
}


def is_env_ready():
  return test_ready_obj['env_ready']


def is_k8s_ready():
  return test_ready_obj['k8s_ready']


def update_readiness(env_ready, k8s_ready):
  test_ready_obj['env_ready'] = env_ready
  test_ready_obj['k8s_ready'] = k8s_ready


class DummyModel(Model):
  pass
