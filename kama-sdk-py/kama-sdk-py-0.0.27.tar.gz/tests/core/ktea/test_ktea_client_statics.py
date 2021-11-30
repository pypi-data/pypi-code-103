import os

import yaml
from k8kat.res.config_map.kat_map import KatMap
from k8kat.utils.testing import ns_factory

from kama_sdk.core.ktea import ktea_client
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.utils.unittest import helper
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestKteaClientStatics(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)
    helper.create_base_kamafile(self.ns)
    if os.path.isfile(ktea_client.tmp_file_mame):
      os.remove(ktea_client.tmp_file_mame)

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish(self.ns)

  def test_kubectl_apply_dry_run_effect(self):
    manifest = good_res(self.ns, '1')
    KteaClient.kubectl_dry_run([manifest])
    self.assertIsNone(KatMap.find('good-1', self.ns))

  def test_kubectl_dry_run_outcomes(self):
    manifest = good_res(self.ns, '1')
    result = KteaClient.kubectl_dry_run([manifest])
    self.assertTrue(result[0])

    valid, error = KteaClient.kubectl_dry_run([
      good_res(self.ns, '1'),
      bad_res(self.ns, '1')
    ])

    self.assertEqual(False, valid)
    self.assertIsNotNone(error)

  def test_kubectl_apply_effect(self):
    manifest = good_res(self.ns, '1')
    KteaClient.kubectl_apply([manifest])
    self.assertIsNotNone(KatMap.find('good-1', self.ns))

  def test_kubectl_apply_outcomes(self):
    outcomes = KteaClient.kubectl_apply([
      good_res(self.ns, '1'),
      bad_res(self.ns, '1')
    ])
    self.assertEqual(2, len(outcomes))
    o1, o2 = outcomes
    self.assertEqual('', o1['api_group'])
    self.assertEqual('', o2['api_group'])

    self.assertEqual('configmap', o1['kind'])
    self.assertEqual('configmaps', o2['kind'])

    self.assertEqual('good-1', o1['name'])
    self.assertEqual('bad-1', o2['name'])

    self.assertEqual('created', o1['verb'])
    self.assertIsNone(o2['verb'])

    self.assertIsNone(o1['error'])
    self.assertIsNotNone(o2['error'])

  def test_short_lived_resfile(self):
    self.assertFalse(os.path.isfile(ktea_client.tmp_file_mame))
    with ktea_client.short_lived_resfile(resdict=dict(foo='bar')):
      with open(ktea_client.tmp_file_mame) as file:
        loaded = yaml.load(file.read())
        self.assertEqual(dict(foo='bar'), loaded)

  def test_filter_res(self):
    res_list = g_res_list(('k1', 'n1'), ('k1', 'n2'))
    selector = ResourceSelector.inflate("expr::k1:n1")
    result = KteaClient.filter_res(res_list, [selector])
    self.assertEqual(result, [res_list[0]])

def g_res(_tuple):
  return dict(
    kind=_tuple[0],
    metadata=dict(
      name=_tuple[1],
      namespace=_tuple[2] if len(_tuple) == 3 else _tuple[1]
    )
  )

def g_res_list(*tuples):
  return [g_res(t) for t in tuples]


good_res = lambda ns, ind: dict(
  apiVersion='v1',
  kind='ConfigMap',
  metadata=dict(namespace=ns, name=f'good-{ind}'),
  data={}
)

bad_res = lambda ns, ind: dict(
  apiVersion='v1',
  kind='ConfigMap',
  metadata=dict(namespace=ns, name=f'bad-{ind}'),
  data='an-invalid-datatype'
)
