import unittest

from kama_sdk.core.core import str_sub


class TestStrSub(unittest.TestCase):

  def test_interp(self):
    callback = lambda s: f"{s}'"
    result = str_sub.interpolate("foo ${bar} and ${baz}", callback)
    self.assertEqual("foo bar' and baz'", result)
