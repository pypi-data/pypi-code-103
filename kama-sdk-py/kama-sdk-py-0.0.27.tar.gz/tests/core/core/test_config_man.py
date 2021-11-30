from datetime import datetime

from kama_sdk.core.core import config_man as cm, config_man_helper, consts
from kama_sdk.core.core.config_man import config_man
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestConfigMan(ClusterTest):

  def test_read_ns(self):
    """
    Rather meaningless but if fails, explains all the other failures.
    :return:
    """
    actual = config_man.get_ns()
    self.assertIsNotNone(actual)

  def test_foo(self):
    actual = config_man.load_source_cmap(reload=True)
    self.assertIsNotNone(actual)

  def test_should_reload_source_integration(self):
    config_man_helper.clear_trackers()
    self.assertTrue(config_man.should_reload_source())

    config_man.get_status()
    self.assertFalse(config_man.should_reload_source())

    config_man.write_status(consts.RUNNING_STATUS)
    self.assertTrue(config_man.should_reload_source())

  def test_read_write_space(self):
    # self.assertEqual({}, config_man.read_space())
    self.assertEqual({}, config_man.read_space(space='s'))

    config_man.write_space({'x': 'y'})
    self.assertEqual({'x': 'y'}, config_man.read_space())
    self.assertEqual({'x': 'y'}, config_man.read_space(reload=True))

    config_man.write_space({'x2': 'y2'}, space='s')
    self.assertEqual({'x2': 'y2'}, config_man.read_space(space='s'))
    self.assertEqual({'x2': 'y2'}, config_man.read_space(space='s', reload=True))
    self.assertEqual({'x': 'y'}, config_man.read_space())
    self.assertEqual({'x': 'y'}, config_man.read_space(reload=True))

  def test_read_write_entry(self):
    config_man.write_entry('k', 'v')
    self.assertEqual('v', config_man.read_space()['k'])

    config_man.write_entry('k2', 'v2', space='b')
    self.assertEqual({'k2': 'v2'}, config_man.read_space(space='b'))

    self.assertEqual('v', config_man.read_entry('k'))
    self.assertEqual('v2', config_man.read_entry('k2', space='b'))

  def test_unset_deep_vars(self):
    original = {'a': {'b': 'c'}, 'a2': 'b2'}
    config_man.patch_user_vars(original)
    self.assertEqual(original, config_man.get_user_vars())
    config_man.unset_user_vars(['a2'])
    self.assertEqual({'a': {'b': 'c'}}, config_man.get_user_vars())

  def test_read_write_user_vars(self):
    config_man.patch_user_vars({"x.y": "x"})
    actual = config_man.get_user_vars()
    self.assertEqual({'x': {'y': 'x'}}, actual)
    self.assertEqual({}, config_man.get_default_vars())
    self.assertEqual({}, config_man.get_publisher_inj_vars())

  def test_typed_read_write_str(self):
    self.typed_read_write_battery(cm.STATUS_KEY, 'foo')

  def test_read_write_bool(self):
    self.typed_read_write_battery(cm.IS_PROTOTYPE_KEY, True)

  def test_read_write_dict(self):
    self.typed_read_write_battery(cm.KTEA_CONFIG_KEY, {'foo': {'bar': ['baz']}})

  def test_read_write_datetime(self):
    self.typed_read_write_battery(cm.update_checked_at_key, datetime.now())

  def typed_read_write_battery(self, key, value):
    config_man.write_typed_entry(key, value)
    actual = config_man.read_typed_entry(key, reload=True)
    self.assertEqual(value, actual)
    with self.assertRaises(RuntimeError):
      config_man.write_typed_entry(key, [value])
    actual = config_man.read_typed_entry(key, reload=True)
    self.assertEqual(value, actual)
