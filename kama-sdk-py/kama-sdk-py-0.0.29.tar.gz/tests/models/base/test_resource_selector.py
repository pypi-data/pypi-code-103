from k8kat.auth.kube_broker import broker

from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.k8s import resource_selector
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.utils.unittest.base_classes import ClusterTest


res_kind = resource_selector.RES_KIND_KEY
res_name = resource_selector.RES_NAME_KEY
label_selector = resource_selector.LABEL_SEL_KEY
field_selector = resource_selector.FIELD_SEL_KEY

class TestResourceSelector(ClusterTest):

  def setUp(self) -> None:
    super(TestResourceSelector, self).setUp()
    ns = config_man.get_ns()
    broker.coreV1.create_namespaced_config_map(ns, pod_one_config)
    broker.coreV1.create_namespaced_config_map(ns, pod_two_config)

  def test_inflate_with_expr(self):
    selector: ResourceSelector = ResourceSelector.inflate("expr::Pod:nginx")
    self.assertEqual("Pod", selector.get_res_kind())
    self.assertEqual("nginx", selector.get_res_name())

  def test_selects_name_matching(self):
    selector = ResourceSelector({
      res_kind: 'ConfigMap',
      res_name: 'pod-one'
    })
    self.assertTrue(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(1, len(selection))
    self.assertEqual('pod-one', selection[0].name)

  def test_selects_name_not_matching(self):
    selector = ResourceSelector({
      res_kind: 'NotConfigMap',
      res_name: 'not-pod-one'
    })
    self.assertFalse(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(0, len(selection))

  def test_selects_res_bad_kind(self):
    selector = ResourceSelector({
      res_kind: 'NotConfigMap',
      label_selector: dict(app='nmachine')
    })
    self.assertFalse(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(0, len(selection))

  def test_selects_res_all_kind(self):
    selector = ResourceSelector({
      res_kind: '*',
      label_selector: dict(app='nmachine')
    })
    self.assertTrue(selector.selects_res(pod_one_config))

  def test_selects_res_right_kind(self):
    selector = ResourceSelector(dict(
      res_kind='ConfigMap',
      label_selector=dict(
        app='nmachine'
      )
    ))
    self.assertTrue(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(2, len(selection))
    self.assertEqual('pod-one', selection[0].name)
    self.assertEqual('pod-two', selection[1].name)

  def test_selects_res_label_selector_not_matching(self):
    selector = ResourceSelector(dict(
      res_kind='ConfigMap',
      label_selector=dict(
        app='nmachine',
        tier='backend'
      )
    ))
    self.assertFalse(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(0, len(selection))

  def test_selects_res_field_selector_matching(self):
    selector = ResourceSelector(dict(
      res_kind='ConfigMap',
      label_selector=dict(
        app='nmachine',
        tier='testware'
      ),
      field_selector={
        'metadata.name': 'pod-one'
      }
    ))
    self.assertTrue(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(1, len(selection))
    self.assertEqual('pod-one', selection[0].name)

  def test_selects_res_field_selector_not_matching(self):
    selector = ResourceSelector(dict(
      res_kind='ConfigMap',
      label_selector=dict(
        app='nmachine',
        tier='testware'
      ),
      field_selector={
        'metadata.name': 'pod-one',
        'metadata.namespace': 'not-the-right-namespace'
      }
    ))
    self.assertFalse(selector.selects_res(pod_one_config))
    selection = selector.query_cluster()
    self.assertEqual(0, len(selection))


pod_one_config = dict(
  kind='ConfigMap',
  metadata=dict(
    name='pod-one',
    labels=dict(
      app='nmachine',
      tier='testware'
    )
  )
)


pod_two_config = dict(
  kind='ConfigMap',
  metadata=dict(
    name='pod-two',
    labels=dict(
      app='nmachine',
      tier='testware'
    )
  )
)

