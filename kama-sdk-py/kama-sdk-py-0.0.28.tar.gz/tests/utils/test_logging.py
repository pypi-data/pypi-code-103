import unittest

from kama_sdk.utils import logging


class TestLogging(unittest.TestCase):
  def test_exception2trace(self):
    try:
      1 / 0
    except ZeroDivisionError as e:
      actual = logging.exception2trace(e)
      self.assertEqual(list, type(actual))
      self.assertEqual('ZeroDivisionError: division by zero', actual[-1])
