from kama_sdk.core.core.config_man import config_man, USER_VARS_LVL
from kama_sdk.model.base import mc
from kama_sdk.model.supplier.base import supplier as sp
from kama_sdk.model.supplier.ext.biz import config_supplier
from kama_sdk.model.supplier.ext.biz.config_supplier import ConfigSupplier
from kama_sdk.utils.unittest.base_classes import ClusterTest

kind = mc.KIND_KEY
idk = mc.ID_KEY
source = sp.SRC_DATA_KEY
output = sp.OUTPUT_FMT_KEY
attr = mc.ATTR_KW

field = config_supplier.FIELD_KEY


class TestConfigSupplier(ClusterTest):

  def setUp(self) -> None:
    super(TestConfigSupplier, self).setUp()
    config_man.patch_def_vars({'def_x': 'x', 'y': 'def_y'})
    config_man.patch_user_vars({'x': 'x', 'y': 'y'})

  def test_resolve_with_field_key(self):
    inst = ConfigSupplier.inflate(no_output_descriptor)
    self.assertEqual({'x': 'x', 'y': 'y'}, inst.resolve())

  def test_resolve_without_field_key(self):
    inst = ConfigSupplier.inflate(x_output_descriptor)
    self.assertEqual('x', inst.resolve())


no_output_descriptor = {output: None, field: USER_VARS_LVL}
x_output_descriptor = {output: '.x', field: USER_VARS_LVL}
