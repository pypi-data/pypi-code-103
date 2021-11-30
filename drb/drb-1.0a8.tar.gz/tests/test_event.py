import unittest
from drb.events import Event

from .utils import DrbTestItem, DrbTestNode

flag = False


class SomeData:
    changed = Event()

    def __init__(self, foo):
        self._foo = foo

    @property
    def foo(self):
        return self._foo

    @foo.setter
    def foo(self, value):
        self._foo = value
        self.changed.notify(self, 'foo', value)


class TestEvent(unittest.TestCase):
    def test_event(self):
        global flag
        flag = False
        my_data = SomeData(42)

        @my_data.changed.register
        def print_it(obj, key, value):
            global flag
            flag = True

        my_data.foo = 10
        self.assertTrue(flag)

    def test_event_drb_item(self):
        item = DrbTestItem("test", None)
        global flag
        flag = False

        @item.changed.register
        def set_run_flag(obj, key, value):
            global flag
            flag = True

        item.name = "new_name"
        self.assertTrue(flag)

    def test_event_drb_node(self):
        node = DrbTestNode(name="test")

        self.assertEqual(node.name, 'test')
        self.assertIsNone(node.value)

        global flag
        flag = False

        @node.changed.register
        def callback_on_changed(obj, key, value):
            global flag
            flag = not flag

        node.name = "new_name"
        self.assertEqual(node.name, 'new_name')
        self.assertTrue(flag)

        node.changed.unregister(callback_on_changed)

        node.name = "very_new_name"
        self.assertEqual(node.name, 'very_new_name')
        self.assertTrue(flag)
