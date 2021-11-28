# pylint: skip-file
import unittest

from ..base import CanonicalException


class LoggingTestCase(unittest.TestCase):

    def test_log_message_formatting(self):
        exc = CanonicalException()
        msg = exc.log(lambda x: x)
        self.assertEqual("Caught fatal %s (id: %s)" % (exc.code, str(exc.id)), msg) 

    def test_log_message_formatting_custom(self):
        exc = CanonicalException()
        msg = exc.log(lambda x: x, 'foo')
        self.assertEqual("foo", msg) 
