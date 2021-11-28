# pylint: skip-file
import unittest

from unimatrix.ext.model import exc


class ExceptionSchemaTestCase(unittest.TestCase):

    def test_serialize_canonical_exception_has_id(self):
        e = exc.CanonicalException()
        dto = e.as_dict()
        self.assertEqual(str(e.id), dto['id'])

    def test_serialize_canonical_exception_has_code(self):
        e = exc.CanonicalException()
        dto = e.as_dict()
        self.assertEqual(e.code, dto['code'])

    def test_serialize_canonical_exception_has_message(self):
        e = exc.CanonicalException()
        dto = e.as_dict()
        self.assertEqual(e.message, dto['message'])

    def test_serialize_canonical_exception_has_detail(self):
        e = exc.CanonicalException()
        dto = e.as_dict()
        self.assertEqual(e.detail, dto['detail'])

    def test_serialize_canonical_exception_has_hint(self):
        e = exc.CanonicalException()
        dto = e.as_dict()
        self.assertEqual(e.hint, dto['hint'])
