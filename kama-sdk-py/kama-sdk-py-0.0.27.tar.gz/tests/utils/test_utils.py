import unittest

from kama_sdk.core.core.types import K8sResSig
from kama_sdk.utils import utils
from kama_sdk.utils.utils import unmuck_primitives


class TestUtils(unittest.TestCase):

  def test_dict_subset_score(self):
    selector = {'kind': 'pod', 'env': ['test', 'dev']}
    challenge1 = {'kind': 'pod'}
    challenge2 = {'kind': 'pod', 'env': 'test'}
    challenge3 = {'kind': 'pod', 'env': 'dev', 'tier': 'app'}
    challenge4 = {'kind': 'pod', 'env': 'prod'}

    self.assertEqual(False, utils.selects_labels(selector, challenge1))
    self.assertEqual(True, utils.selects_labels(selector, challenge2))
    self.assertEqual(True, utils.selects_labels(selector, challenge3))
    self.assertEqual(False, utils.selects_labels(selector, challenge4))

  def test_relaxed_subdict(self):
    actual = utils.relaxed_subdict({'a': 1, 'b': 2}, 'a', 'c')
    self.assertEqual({'a': 1, 'c': None}, actual)

  def test_strict_subdict(self):
    actual = utils.subdict({'a': 1, 'b': 2}, 'a', 'c')
    self.assertEqual({'a': 1}, actual)

  def test_flat2deep(self):
    actual = utils.flat2deep({'a': 'b'})
    self.assertEqual({'a': 'b'}, actual)

    actual = utils.flat2deep({'a.b': 'c'})
    self.assertEqual({'a': {'b': 'c'}}, actual)

    actual = utils.flat2deep({'a': {'b': 'c'}})
    self.assertEqual({'a': {'b': 'c'}}, actual)

    actual = utils.flat2deep({'a': {'b.c': 'd'}})
    self.assertEqual({'a': {'b.c': 'd'}}, actual)

    actual = utils.flat2deep({'a': {'b.c': ['d']}})
    self.assertEqual({'a': {'b.c': ['d']}}, actual)

  def test_any2bool(self):
    self.assertTrue(utils.any2bool(True))
    self.assertTrue(utils.any2bool('True'))
    self.assertTrue(utils.any2bool('true'))
    self.assertTrue(utils.any2bool('yes'))
    self.assertTrue(utils.any2bool('nectar'))
    self.assertTrue(utils.any2bool(1))

    self.assertFalse(utils.any2bool(False))
    self.assertFalse(utils.any2bool('False'))
    self.assertFalse(utils.any2bool('false'))
    self.assertFalse(utils.any2bool('no'))
    self.assertFalse(utils.any2bool(''))
    self.assertFalse(utils.any2bool(0))
    self.assertFalse(utils.any2bool(None))

  def test_deep_get2(self):
    src = {'x': 'y'}
    self.assertEqual(src, utils.deep_get(src, ''))

    src = {'x': 'y'}
    self.assertEqual('y', utils.deep_get(src, 'x'))

    src = {'x': 'y'}
    self.assertEqual(None, utils.deep_get(src, 'x2'))

    src = {'x': {'x': 'y'}}
    self.assertEqual('y', utils.deep_get(src, 'x.x'))

    src = {'x': {'x': 'y'}}
    self.assertEqual({'x': 'y'}, utils.deep_get(src, 'x'))

    src = {'x': {'x': 'y'}}
    self.assertEqual(None, utils.deep_get(src, 'x.x2'))

  def test_deep_set(self):
    root = dict(x='x', y='y')
    utils._deep_set(root, ['x'], 'y')
    self.assertEqual(root, dict(x='y', y='y'))

    root = dict(x=dict(x='x', y='y'), y='y')
    utils._deep_set(root, ['x', 'x'], 'y')
    expect = dict(x=dict(x='y', y='y'), y='y')
    self.assertEqual(root, expect)

    root = dict()
    utils._deep_set(root, ['x', 'x'], 'x')
    self.assertEqual(root, dict(x=dict(x='x')))

  def test_dict_to_keyed(self):
    actual = utils.dict2keyed(dict(
      bar='foo',
      foo=dict(
        bar='baz',
        foo=dict(bar='baz')
      )
    ))
    expected = [('bar', 'foo'), ('foo.bar', 'baz'), ('foo.foo.bar', 'baz')]
    self.assertEqual(expected, actual)

  def test_hybrid_dict_to_keyed(self):
    actual = utils.dict2keyed({
      'foo.bar': 'baz',
      'bar.foo': 'zab'
    })

    expected = [('foo.bar', 'baz'), ('bar.foo', 'zab')]
    self.assertEqual(expected, actual)

  def test_are_res_same_true(self):
    r1 = K8sResSig(kind='pod', name='p1')
    r2 = K8sResSig(kind='pod', name='p1')
    self.assertTrue(utils.are_res_same(r1, r2))

    r2 = K8sResSig(kind='Pod', name='p1')
    self.assertTrue(utils.are_res_same(r1, r2))

    r2 = K8sResSig(kind='pods', name='p1')
    self.assertTrue(utils.are_res_same(r1, r2))

  def test_are_res_same_false(self):
    r1 = K8sResSig(kind='pod', name='p1')
    r2 = K8sResSig(kind='job', name='p1')
    self.assertFalse(utils.are_res_same(r1, r2))

    r2 = K8sResSig(kind='pod', name='p2')
    self.assertFalse(utils.are_res_same(r1, r2))

  def test_kao2log(self):
    self.assertEqual("apps.deployment/foo created", utils.kao2log(dict(
      api_group='apps',
      kind='deployment',
      name='foo',
      verb='created'
    )))

    self.assertEqual("pod/bar unchanged", utils.kao2log(dict(
      api_group='',
      kind='pod',
      name='bar',
      verb='unchanged'
    )))

    self.assertEqual("pod/baz error text", utils.kao2log(dict(
      kind='pod',
      name='baz',
      error='error text'
    )))

  def test_log2ktlapplyoutcome(self):
    log = "pod/foo created"
    result = utils.log2kao(log)
    self.assertEqual('pod', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('created', result['verb'])
    self.assertEqual('', result['api_group'])

    log = "deployment.apps/foo created"
    result = utils.log2kao(log)
    self.assertEqual('deployment', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('created', result['verb'])
    self.assertEqual('apps', result['api_group'])

    log = "role.rbac.authorization.k8s.io/foo unchanged"
    result = utils.log2kao(log)
    self.assertEqual('role', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('unchanged', result['verb'])
    self.assertEqual('rbac.authorization.k8s.io', result['api_group'])

  def test_unmuck_primitives(self):
    actual = 'foo'
    self.assertEqual(actual, unmuck_primitives(actual))

    actual = dict(x='y')
    self.assertEqual(actual, unmuck_primitives(actual))

    actual = dict(x=0)
    self.assertEqual(actual, unmuck_primitives(actual))

    actual, exp = dict(x='0'), dict(x=0)
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [dict(x='0')], [dict(x=0)]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [[0], '0'], [[0], 0]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [dict(x=['false'])], [dict(x=[False])]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual = dict(x=[[dict(x=False)]], y=[True])
    self.assertEqual(actual, unmuck_primitives(actual))
