from kama_sdk.model.base import mc
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.supplier.base import supplier as sup
from kama_sdk.model.supplier.base import expr2config as mod
from kama_sdk.model.supplier.base.special_suppliers import DelayedInflateSupplier, SelfSupplier
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.unittest.base_classes import KamaTest

kind = mc.KIND_KEY
idk = mc.ID_KEY
source = sup.SRC_DATA_KEY
output = sup.OUTPUT_FMT_KEY
serializer = sup.SERIALIZER_KEY


class TestExpr2Config(KamaTest):

  def test_tokenize(self):
    self.assertEqual(['abc'], mod.tokenize('abc'))
    self.assertEqual(['a>bc'], mod.tokenize('a>bc'))
    self.assertEqual(['a', '>>', 'bc'], mod.tokenize('a>>bc'))
    self.assertEqual(['a | b', '>>', 'c'], mod.tokenize('a | b>>c'))
    self.assertEqual(
      ['w', '->', 'x', '>>', 'y', '=>', 'z'],
      mod.tokenize("w->x>>y=>z")
    )

  def test_tokens2tree_single(self):
    self.assertEqual({
      kind: Supplier.__name__,
      mc.INHERIT_KEY: 'foo',
    }, mod.tokens2tree(['foo']))

  def test_tokens2tree_single_kind(self):
    self.assertEqual({
      kind: 'Foo',
    }, mod.tokens2tree(['kind::Foo']))

  def test_tokens2tree_double(self):
    self.assertEqual({
      kind: Supplier.__name__,
      mc.INHERIT_KEY: 'foo',
      serializer: sup.SER_JQ,
      output: 'bar',
    }, mod.tokens2tree(['foo', '->', 'bar']))

  def test_tokens2tree_triple(self):
    self.assertEqual({
      kind: Supplier.__name__,
      serializer: sup.SER_JQ,
      output: 'baz',
      source: {
        kind: Supplier.__name__,
        mc.INHERIT_KEY: 'foo',
        serializer: sup.SER_NATIVE,
        output: 'bar'
      }
    }, mod.tokens2tree(['foo', '=>', 'bar', '->', 'baz']))

  def test_tokens2tree_with_ref_single(self):
    models_manager.add_descriptors([roth])
    result = mod.tokens2tree(["&referenced"])
    expect = {
      kind: DelayedInflateSupplier.__name__,
      source: 'referenced'
    }
    self.assertEqual(expect, result)

  def test_tokens2tree_with_ref_double(self):
    models_manager.add_descriptors([roth])

    expect = {
      kind: DelayedInflateSupplier.__name__,
      source: 'referenced',
      serializer: sup.SER_MODEL_ATTR,
      output: 'foo'
    }

    result = mod.tokens2tree(["&referenced", ">>", "foo"])
    self.assertEqual(expect, result)

    result = mod.tokens2tree(["&id::referenced", ">>", "foo"])
    self.assertEqual(expect, result)

  def test_tokens2tree_with_kind_ref_double(self):
    models_manager.add_descriptors([roth])

    expect = {
      kind: DelayedInflateSupplier.__name__,
      source: {
        kind: 'Referenced'
      },
      serializer: sup.SER_MODEL_ATTR,
      output: 'foo'
    }

    result = mod.tokens2tree(["&kind::Referenced", ">>", "foo"])
    self.assertEqual(expect, result)

  def test_expr2config(self):
    self.assertEqual({
      kind: Supplier.__name__,
      serializer: sup.SER_NATIVE,
      output: 'z',
      source: {
        kind: Supplier.__name__,
        serializer: sup.SER_MODEL_ATTR,
        output: 'y',
        source: {
          kind: SelfSupplier.__name__,
          serializer: sup.SER_JQ,
          output: 'x'
        }
      }
    }, mod.expr2config("self->x>>y=>z"))


roth = {
  kind: Supplier.__name__,
  mc.ID_KEY: "referenced",
  'foo': 'bar'
}
