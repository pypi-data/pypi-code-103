# pylint: skip-file
import unittest

from .. import ValidationError
from ..schema import CanonicalExceptionSchema


class ValidationErrorTestCase(unittest.TestCase):

    def test_create_from_marshmallow_exception(self):
        schema = CanonicalExceptionSchema()
        try:
            schema.load({})
        except Exception as e:
            exc = ValidationError(spec=e.normalized_messages())
            dto = exc.as_dict()
            self.assertIn('spec', dto)
        else:
            self.fail()
